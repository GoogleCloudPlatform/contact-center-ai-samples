/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */
const helpers = require('./helpers');

exports.cxPrebuiltAgentsTelecom = (req, res) => {
  console.log('Cloud Function:', 'Invoked cloud function from Dialogflow');
  const tag = req.body.fulfillmentInfo.tag;

  if (tag) {
    switch (tag) {
      //BEGIN detectCustomerAnomaly
      case 'detectCustomerAnomaly': {
        console.log(tag + ' was triggered.');
        const phone_number = req.body.sessionInfo.parameters.phone_number;
        const bill_month = req.body.sessionInfo.parameters.bill_state;
        const parameters = req.body.sessionInfo.parameters;
        const agentId = req.body.payload.fields.agentId;
        const flowId = req.body.payload.fields.flowId;
        let targetPage = req.body.payload.fields.show_bill_details_page_id;
        let bill_amount;
        let product_line;
        let anomaly_detect = 'false';
        let purchase = 'The Godfather';
        let purchase_amount = 9.99;
        let total_bill_amount = 64.33;
        const bill_without_purchase = 54.34;
        const updated_parameters = {};

        const [month_name, first_of_month, last_month_name] =
          helpers.get_date_details(bill_month);
        console.log(month_name, first_of_month, last_month_name);

        // Getting the month name based on the bill state - current or previous
        // For example, if the current month is December, we get the values as
        // December, December 1st, November

        // Only 999999 will have anomaly detection
        if (phone_number.toString() === '9999999999') {
          anomaly_detect = 'true';
          product_line = 'phone';
          purchase = 'device protection';
          updated_parameters['product_line'] = product_line;
          updated_parameters['bill_month'] = month_name;
          updated_parameters['last_month'] = last_month_name;
          targetPage =
            req.body.payload.fields.suggest_service_cancellation_page_id;
        }

        // If bill hike amount is given - we just add it to the total bill
        if ('bill_amount' in parameters) {
          bill_amount = parameters['bill_amount'];
          purchase_amount = bill_amount['amount'];
          total_bill_amount = 54.34 + purchase_amount;
        }

        // Adding the updated session parameters to the new parameters json
        updated_parameters['anomaly_detect'] = anomaly_detect;
        updated_parameters['purchase'] = purchase;
        updated_parameters['purchase_amount'] = purchase_amount;
        updated_parameters['bill_without_purchase'] = bill_without_purchase;
        updated_parameters['total_bill'] = total_bill_amount;
        updated_parameters['first_month'] = first_of_month;

        res.status(200).send({
          fulfillmentResponse: {
            messages: [
              {
                text: {
                  text: `Thanks! I'm going to pull up your ${bill_month} bill. The billing period began on ${updated_parameters['first_month']}.`,
                },
              },
            ],
          },
          sessionInfo: {
            parameters: updated_parameters,
          },
          targetPage: `${agentId}/flows/${flowId}/pages/${targetPage}`,
        });
        break;
      }
      // BEGIN validatePhoneLine
      case 'validatePhoneLine': {
        console.log(tag + ' was triggered.');
        const paramRequired =
          req.body.pageInfo.formInfo.parameterInfo[0].required;
        let phone = req.body.pageInfo.formInfo.parameterInfo[0].value;
        let parameter_state = 'VALID';
        let fulfillmentMessage = 'Thanks for providing your phone number!';
        let phone_line_verified;
        let line_index;
        let domestic_coverage;
        const covered_lines = [
          '5555555555',
          '5105105100',
          '1231231234',
          '9999999999',
        ];

        if (!covered_lines.includes(phone)) {
          parameter_state = 'INVALID';
          fulfillmentMessage =
            'Sorry, we do not recognize that number. Please try again later!';
          // we will reset the session parameter to 'null' so that the user can re-enter a new phone number
          phone = null;
        }

        // Loop over the covered lines array
        covered_lines.forEach((line, index) => {
          // For each phone line in the array, check if the last 4 digits are
          // included in the string. when true, update the line_index variable
          if (line.includes(phone)) {
            line_index = index;
            console.log('This is the index ' + line_index);
          }
        });

        // Only 9999 will fail;
        if (line_index === 3) {
          phone_line_verified = 'false';
        } else {
          phone_line_verified = 'true';
        }

        // Only 1234 will have domestic coverage.
        if (line_index === 2) {
          domestic_coverage = 'true';
        } else {
          domestic_coverage = 'false';
        }

        res.status(200).send({
          fulfillmentResponse: {
            messages: [
              {
                text: {
                  text: [fulfillmentMessage],
                },
              },
            ],
          },
          pageInfo: {
            formInfo: {
              parameterInfo: [
                {
                  displayName: 'phone_number',
                  required: paramRequired,
                  state: parameter_state,
                },
              ],
            },
          },
          sessionInfo: {
            parameters: {
              phone_line_verified: phone_line_verified,
              domestic_coverage: domestic_coverage,
              phone: phone,
            },
          },
        });
        break;
      }
      // BEGIN cruisePlanCoverage
      case 'cruisePlanCoverage': {
        console.log(tag + ' was triggered.');

        const port = req.body.sessionInfo.parameters.destination;
        let port_is_covered;
        let parameter_state;
        // Sample list of covered cruise ports.
        const covered_ports = ['mexico', 'canada', 'anguilla'];

        if (covered_ports.includes(port.toLowerCase())) {
          port_is_covered = 'true';
          parameter_state = 'VALID';
        } else {
          port_is_covered = 'false';
          parameter_state = 'INVALID';
        }

        res.status(200).send({
          pageInfo: {
            formInfo: {
              parameterInfo: [
                {
                  displayName: 'destination',
                  state: parameter_state,
                },
              ],
            },
          },
          sessionInfo: {parameters: {port_is_covered: port_is_covered}},
        });
        break;
      }
      // BEGIN internationalCoverage
      case 'internationalCoverage': {
        console.log(tag + ' was triggered.');
        const destination = req.body.sessionInfo.parameters.destination;
        let coverage;
        // Sample list of covered international monthly destinations.
        const covered_by_monthly = [
          'anguilla',
          'australia',
          'brazil',
          'canada',
          'chile',
          'england',
          'france',
          'india',
          'japan',
          'mexico',
          'russia',
          'singapore',
        ];
        // Sample list of covered international daily destinations.
        const covered_by_daily = [
          'anguilla',
          'australia',
          'brazil',
          'canada',
          'chile',
          'england',
          'france',
          'india',
          'japan',
          'mexico',
          'singapore',
        ];

        if (
          covered_by_monthly.includes(destination.toLowerCase()) &&
          covered_by_daily.includes(destination.toLowerCase())
        ) {
          coverage = 'both';
        } else if (
          covered_by_monthly.includes(destination.toLowerCase()) &&
          !covered_by_daily.includes(destination.toLowerCase())
        ) {
          coverage = 'monthly_only';
        } else if (
          !covered_by_monthly.includes(destination.toLowerCase()) &&
          !covered_by_daily.includes(destination.toLowerCase())
        ) {
          coverage = 'neither';
        } else {
          // This should never happen, because covered_by_daily is a subset of
          // covered_by_monthly
          coverage = 'daily_only';
        }

        res.status(200).send({sessionInfo: {parameters: {coverage: coverage}}});
        break;
      }
      // BEGIN cheapestPlan
      case 'cheapestPlan': {
        console.log(tag + ' was triggered.');
        const trip_duration = req.body.sessionInfo.parameters.trip_duration;
        let monthly_cost;
        let daily_cost;
        let suggested_plan;

        // Can only suggest cheapest if both are valid for location.

        // When trip is longer than 30 days, calculate per-month cost (example $
        // amounts). Suggest monthly plan.
        if (trip_duration > 30) {
          monthly_cost = Math.floor(trip_duration / 30) * 70;
          daily_cost = trip_duration * 10;
          suggested_plan = 'monthly';
        }
        // When trip is <= 30 days, but greater than 6 days, calculate monthly
        // plan cost and daily plan cost. Suggest monthly b/c it is the cheaper
        // one.
        else if (trip_duration <= 30 && trip_duration > 6) {
          monthly_cost = 70;
          daily_cost = trip_duration * 10;
          suggested_plan = 'monthly';
        }
        // When trip is <= 6 days, calculate daily plan cost. Suggest daily
        // plan.
        else if (trip_duration <= 6 && trip_duration > 0) {
          monthly_cost = Math.floor(trip_duration / 30) * 70;
          daily_cost = trip_duration * 10;
          suggested_plan = 'daily';
        } else {
          // This should never happen b/c trip_duration would have to be
          // negative
          suggested_plan = 'null';
        }

        res.status(200).send({
          sessionInfo: {
            parameters: {
              monthly_cost: monthly_cost,
              daily_cost: daily_cost,
              suggested_plan: suggested_plan,
            },
          },
        });
        break;
      }
      default: {
        console.log('default case called');
        res.status(200).end();
        break;
      }
    }
  }
};
