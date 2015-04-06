# backend-333
Back end for COS 333 project

TODO list:

General:
    Investigate way to send notifications without push notification (for group invites)

Views:
create event - David
create group - David
event search - Blake
    public vs private
user search  - Blake
Make module with error messages - Blake
Find way to avoid making everything csrf_exempt
Figure out how to avoid plaintext passwords

Later TODOS:
create invites

Create-Event fields:
    title (Mandatory)
    public
    time (Mandatory)
    age_restrictions
    price
    description
    invite_list (Array of Names)

Notes on event querying:
    Lance/Graham need a way to get events that are related to specific users (i.e. events user is going to, events user created, and events user is invited to). Therefore, make new api at /events/get that takes post request with parameters: username=test@test.com, type=invited, type=created, type=attending. When making the api call, any combination of the three types will be included and we will return up to three JSONs that correspond to the request parameters. The JSON will be returned in the form [{"invited": [\<JSON with events user is invited to\>], "attending": [\<JSON with events the user is attending\>], "created": [\<JSON with events the user created\>]}]. Note that only the requested fields will be included in the JSON that is returned.
