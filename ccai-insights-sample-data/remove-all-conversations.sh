# Bash script to delete all conversations in Insights

PROJECT_ID="your-project-id"
LOCATION="us-central1"
PAGESIZE="100"

echo "Loading conversations..."
CONVERSATION_IDS=$(curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json; charset=utf-8" \
"https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations?pageSize=$PAGESIZE" \
| jq -c '.[] | .[]? | .name' | sed -e 's/^"//' -e 's/"$//')

counter="0"
until [ ${#CONVERSATION_IDS} -lt 1 ];
do
  for i in $CONVERSATION_IDS;
  do
    echo "Deleting conversation:" $i;
    curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" -d "{force: true}" \
    "https://contactcenterinsights.googleapis.com/v1/$i" &
    counter=$[$counter+1]
  done;
  wait
  echo "Loading conversations..."
  CONVERSATION_IDS=$(curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://contactcenterinsights.googleapis.com/v1/projects/$PROJECT_ID/locations/$LOCATION/conversations?pageSize=$PAGESIZE" \
  | jq -c '.[] | .[]? | .name' | sed -e 's/^"//' -e 's/"$//')
done
echo "Deleted" $counter "conversations."
