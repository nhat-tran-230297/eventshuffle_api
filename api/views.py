import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Event, Date, Participant
from .utils import is_date_valid, has_dates_duplicate


# Create your views here.

def home_page(request):
    """
    Displays UI for all requests
    """
       # used for easily rendering index.html
    request_methods = [
        # List all events 
        {
            "title": "List all events",
            "name": "list-all-events",
            "endpoints": "/api/v1/event/list",
            "method": "get",
            "button_type": "btn-primary",
            "parameters": False
        }, 

        # Create an event
        {
            "title": "Create an event",
            "name": "create-an-event",
            "endpoints": "/api/v1/event",
            "method": "post",
            "button_type": "btn-success",
            "parameters": ["Body"]
        },

        # Show an event
        {
            "title": "Show an event",
            "name": "show-an-event",
            "endpoints": "/api/v1/event/{id}",
            "method": "get",
            "button_type": "btn-primary",
            "parameters": ["id"]
        },
        
        # Add votes to an event
        {
            "title": "Add votes to an event",
            "name": "add-votes-to-event",
            "endpoints": "/api/v1/event/{id}/vote",
            "method": "post",
            "button_type": "btn-success",
            "parameters": ["id", "Body"]
        },

        # Show the results of an event
        {
            "title": "Show the results of an event",
            "name": "show-results-of-event",
            "endpoints": "/api/v1/event/{id}/results",
            "method": "get",
            "button_type": "btn-primary",
            "parameters": ["id"]
        },

        # Delete an event 
        {
            "title": "Delete an event",
            "name": "delete-an-event",
            "endpoints": "/api/v1/event/{id}/delete",
            "method": "delete",
            "button_type": "btn-danger",
            "parameters": ["id"]
        } 
    ]

    return render(request, 'api/index.html', {'request_methods': request_methods})


def list_all_events(request):
    """ 
    List all events 
    """
    events = Event.objects.all()

    event_json = { 'events' :
                                [
                                    {
                                        "id": event.id, 
                                        "name": event.name
                                    } 
                                    for event in events
                                ]
                }

    return JsonResponse(event_json, status=200, json_dumps_params={'indent': 2})


def create_event(request):
    """ 
    Create an event 
    """
    # retrieves request input via AJAX call
    responseBody = request.POST.get('responseBody')

    # handle error when user enters invalid JSON format
    try:
        responseBodyJSON = json.loads(responseBody)
    except json.decoder.JSONDecodeError:
        return JsonResponse({"error": "invalid input"}, status=404, json_dumps_params={'indent': 2})


    # get valid request input 
    name = responseBodyJSON.get('name')
    dates = responseBodyJSON.get('dates')

    if not name:
        return JsonResponse({"error": "'name' missing"}, status=404, json_dumps_params={'indent': 2})

    if not dates:
        return JsonResponse({"error": "'dates' missing"}, status=404, json_dumps_params={'indent': 2})

    if not has_dates_duplicate(dates):
        return JsonResponse({"error": "find duplicate dates"}, status=404, json_dumps_params={'indent': 2})


    # interact with database
    event = Event(name=name)
    event.save()
    for date in dates:
        # validate the datetime format of input
        if not is_date_valid(date):
            return JsonResponse({"error": f"Invalid date '{date}'. Date format should be yyyy-mm-dd"}, status=404, json_dumps_params={'indent': 2})

        new_date = Date(date_format=date, event=event)
        new_date.save()


    event_json = {'': 'create', 'id': event.id}
    return JsonResponse(event_json, status=200, json_dumps_params={'indent': 2})


def show_event(request, id):
    """ 
    Show an event 
    """
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"error": f"Event {id} does not exist"}, status=404, json_dumps_params={'indent': 2})

    # response body
    event_json = {
                    "id": event.id,
                    "name": event.name,
                    "dates": [date.date_format for date in event.dates.all()],
                    "votes": [
                                {
                                    "date": date.date_format,
                                    "people": [p.name for p in date.participants.all()]
                                } 
                                for date in event.dates.all()
                            ]
                }

    return JsonResponse(event_json, status=200, json_dumps_params={'indent': 2})



@csrf_exempt
def add_vote(request, id):
    """ 
    Add votes to an event 
    """
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"error": f"Event {id} does not exist"}, status=404, json_dumps_params={'indent': 2})

    # retrieves request input via AJAX call
    responseBody = request.POST.get('responseBody')

    # handle error when user enters invalid JSON format
    try:
        responseBodyJSON = json.loads(responseBody)
    except json.decoder.JSONDecodeError:
        return JsonResponse({"error": "invalid input"}, status=404, json_dumps_params={'indent': 2})

    # get valid request input
    name = responseBodyJSON.get('name')
    votes = responseBodyJSON.get('votes')

    # validate request input
    if not name:
        return JsonResponse({"error": "'name' missing"}, status=404, json_dumps_params={'indent': 2})

    if not votes:
        return JsonResponse({"error": "'dates' missing"}, status=404, json_dumps_params={'indent': 2})

    if not has_dates_duplicate(votes):
        return JsonResponse({"error": "find duplicate dates"}, status=404, json_dumps_params={'indent': 2})

    # interact with database
    participant = Participant(name=name)  
    participant.save()

    # use hash map (key: date, value: index of date) to reduce time complexity
    date_index_map = {date.date_format: index for index, date in enumerate(event.dates.all())}  

    for vote in votes:

        # validate the datetime format of input
        if not is_date_valid(vote):
            return JsonResponse({"error": f"Invalid date '{vote}'. Date format should be yyyy-mm-dd"}, status=404, json_dumps_params={'indent': 2})

        # validate whether user votes for date that exists in the event
        index = date_index_map.get(vote)
        if index is None:
            return JsonResponse({"error": f"date {vote} does not exist"}, status=404, json_dumps_params={'indent': 2})

        date = event.dates.all()[index]
        date.participants.add(participant)

    # response body
    event_json = {
        "id": event.id,
        "name": event.name,
        "dates": [date.date_format for date in event.dates.all()],
        "votes": [
                    {
                        "date": date.date_format,
                        "people": [p.name for p in date.participants.all()]
                    } 
                    for date in event.dates.all()
                ]
    }

    return JsonResponse(event_json, status=200, json_dumps_params={'indent': 2})


def show_results(request, id):
    """ 
    Show the results of an event 
    """

    # requested event not exist
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"error": f"Event {id} does not exist"}, status=404, json_dumps_params={'indent': 2})

    
    # get the most suitable date
    # if there are more than 1 suitable dates, display them all
    max_num_people = max([date.participants.count() for date in event.dates.all()])
    suitable_dates = [date for date in event.dates.all() if date.participants.count() == max_num_people]

    # response body
    results_json = {
        "id": id,
        "name": event.name,
        "suitable_datess": [
                            {
                                "date": suitable_date.date_format,
                                "people": [p.name for p in suitable_date.participants.all()]
                            }
                            for suitable_date in suitable_dates
                        ]
    }

    return JsonResponse(results_json, status=200, json_dumps_params={'indent': 2})

@csrf_exempt
def delete_event(request, id):
    """ 
    Delete an event 
    """
    # requested event not exist
    try:
        event = Event.objects.get(pk=id)
    except Event.DoesNotExist:
        return JsonResponse({"error": f"Event {id} does not exist"}, status=404, json_dumps_params={'indent': 2})

    event_json = {'': 'delete', "id": event.id}

    event.delete()

    return JsonResponse(event_json, status=200, json_dumps_params={'indent': 2})