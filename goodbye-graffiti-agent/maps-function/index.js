/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */

 var axios = require('axios');

 exports.lookupPlace = async (req, res) => {
    
    let tag = req.body.fulfillmentInfo.tag;
    var payload = {};
    var caller_id = '<no-number>';
    var channel;

    if (!!tag) {
        switch (tag) {
            //BEGIN findPlace
            
                case 'geocode':
                  console.log(tag + ' was triggered.');
                  var results = [];
                  
                  // Check if required params have been populated
                  if (!(req.body.sessionInfo && req.body.sessionInfo.parameters)) {
                    return res.status(404).send({ error: 'Not enough information.' });
                  }

                  // Retrieve caller_id if it's a phone call 
                  if ( typeof req.body.payload !== 'undefined' && req.body.payload !== 'undefined' ) {
                    caller_id = req.body.payload.telephony.caller_id; 
                  }
                   
                  // Set location to the location param value collected from the user. 
                  // Location must be a place name or an address. Reserved characters (for example the plus sign "+") must be URL-encoded. 
                  location = encodeURI(req.body.sessionInfo.parameters['location'].original);
                  
                  // Identify channel to generate the right response payload
                  channel = req.body.sessionInfo.parameters['channel'];

                  console.log('caller_id: ' + caller_id);
                  
                  // invokes Geocode APIs and looks for a match
                  try {
                      var config = {
                        method: 'get',
                        url: 'https://maps.googleapis.com/maps/api/geocode/json?address=' + location + '&key=YOUR_API_KEY',
                        headers: { }
                      };
                          
                      axios(config)
                      .then(function (response) {
                        //at least one result
                        if(response.data.results.length > 0) {

                          for(var i in response.data.results){
                            // geocoder returned several results
                            var result = response.data.results[i];
                            results.push(result);
                          }
                          
                          // single match scenario. Build map. Either ways transition to the same target page. Disambiguation in Dialogflow
                          if (results.length == 1){
                            var lat = results[0].geometry.location.lat;
                            var lng = results[0].geometry.location.lng;
                            var formatted_address = results[0].formatted_address;
                            
                            // call companion payload
                            if(channel == "call-companion") {
                              // config static map
                              var map_img = 'https://maps.googleapis.com/maps/api/staticmap?center=' + formatted_address + '&zoom=14&size=600x300&markers=color:red|' + lat + ',' + lng +'&key=YOUR_API_KEY'
                              payload = {
                                "richContent": [
                                  {
                                    "type": "image",
                                    "imageUrl": map_img
                                  }
                                ]
                              };
                            }  
                            
                            // df-messenger payload  
                            if(channel == "df-messenger"){ 
                              payload = {
                                "richContent": [
                                  [
                                    {
                                      "type": "image",
                                      "rawUrl": map_img,
                                      "accessibilityText": "Map image"
                                    }
                                  ]
                                ]
                              };
                            }  
                            
                          } 
                          
                        } else {
                          //handle ZERO_RESULTS
                          formatted_address = "";
                        }
                        // send fullfilment back to agent
                        res.status(200).send({
                          sessionInfo: {
                            parameters: {
                              formatted_address: formatted_address,
                              caller_id: caller_id
                            }
                          },
                          fulfillmentResponse: {
                            messages: [{
                              payload: payload
                            }]
                          }
                        }); 
                      });
                      
                    } catch (error) {
                      res.status(500).send(error);
                      console.log(error);
                    }
                  
                  break;
  
  

            default:
                console.log('default case called');
                res.status(200).end();
                break;
        }
    }
};
  