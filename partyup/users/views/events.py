from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from users.models import Event, User_Profile
from datetime import date


@csrf_exempt
def event_search(request):
    '''
    Client sends a POST request that includes information to be searched on.
    Possible information the requst can include is title, public, location
    (not implemented yet), date/time, age, price, category (not implemented
    yet), and description.
    '''
    response = {}
    # Check for errors in the function call
    if request.method != 'POST':
        response['error'] = 'NOT A POST REQUEST'
        response['accepted'] = False
        return JsonResponse(response)
    if not request.user.is_authenticated():
        response['error'] = 'User is not logged in'
        response['accepted'] = False
        return JsonResponse(response)

    # Parse request and return search results
    query = Event.objects.all()

    # TODO: there should probabily be some kind of sanitization here
    if 'title' in request.POST:
        query = query.filter(title__icontains=request.POST['title'])
    if 'public' in request.POST:
        # requests.POST['public'] should be either 0 or 1
        query = query.filter(public=int(request.POST['public']))
    if 'location' in request.POST:
        pass    # TODO
    if 'date' in request.POST:
        # Parse datetime object from request
        # Date should be formatted as follows:
        # YYYYMMDDhhmm
        year = int(request.POST['date'][:4])
        month = int(request.POST['date'][4:6])
        day = int(request.POST['date'][6:8])
        query = query.filter(time__startswith=date(year, month, day))
    if 'age' in request.POST:
        query = query.filter(age_restrictions__lte=int(request.POST['age']))
    if 'price' in request.POST:
        query = query.filter(price__lte=int(request.POST['price']))
    if 'category' in request.POST:
        pass    # TODO
    if 'description' in request.POST:
        query = query.filter(description__icontains=request.POST['description'])

    results = []
    for entry in query:
        # Remove unnecessary fields from query results
        entry = entry.to_dict()
        entry.pop('attending_list', None)
        entry.pop('created_by', None)

        # Replace foreign keys with actual names/values
        invited = entry.pop('invite_list', None)
        invited_detail = []
        for invitee in invited:
            user_profile = User_Profile.objects.get(pk=invitee.id)
            detail = {
                'id': invitee.id,
                'username': user_profile.user.username,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name
            }
            invited_detail.append(detail)
        entry['invite_list'] = invited_detail

        admin = entry.pop('admin', None)
        admin = User_Profile.objects.get(pk=admin.id)
        admin_detail = {
            'id': admin.id,
            'username': admin.user.username,
            'first_name': admin.user.first_name,
            'last_name': admin.user.last_name
        }
        entry['admin'] = admin_detail

        # Save the updated entry
        results.append(entry)

    # Return results
    response['accepted'] = True
    response['results'] = results

    return JsonResponse(response)
