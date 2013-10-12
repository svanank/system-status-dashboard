#
# Copyright 2013 - Tom Alessi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""This module contains all of the configuration functions of ssd"""


from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib import messages
from ssd.main.models import Service
from ssd.main.models import Event_Service
from ssd.main.forms import AddServiceForm
from ssd.main.forms import RemoveServiceForm, ModifyServiceForm


@login_required
@staff_member_required
def services(request):
    """View and Add Services
 
    """

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':
       
        # Check the form elements
        form = AddServiceForm(request.POST)

        if form.is_valid():
            service = form.cleaned_data['service']

            # Don't allow duplicates
            try:
                Service(service_name=service).save()
            except IntegrityError:
                pass


            messages.add_message(request, messages.SUCCESS, 'Service saved successfully')

            # Send them back so they can see the newly created email addresses
            # incident
            return HttpResponseRedirect('/admin/services')

        else:
            messages.add_message(request, messages.ERROR, 'Invalid data entered, please correct the errors below:')

    # Not a POST
    else:
        # Create a blank form
        form = AddServiceForm()
    
    # Obtain all current email addresses
    services = Service.objects.values('id','service_name')
    
    # Print the page
    return render_to_response(
       'services/services.html',
       {
          'title':'System Status Dashboard | Manage Services',
          'form':form,
          'services':services,
          'breadcrumbs':{'Admin':'/admin','Manage Services':'services'},
          'nav_section':'services',
          'nav_sub':'services'
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def service_delete(request):
    """Remove Service"""

    # If this is a POST, then validate the form and save the data, otherise send them
    # to the main services page
    if request.method == 'POST':
        
        # Check the form elements
        form = RemoveServiceForm(request.POST)

        if form.is_valid():
            id = form.cleaned_data['id']
            # Remove the services
            
            # If this service is currently tied to incidents or maintenances,
            # Do not allow them to be deleted w/o removing them from the relevant
            # services first


            # Part of any incidents or maintenances?
            if Event_Service.objects.filter(service_id=id):
                messages.add_message(request, messages.ERROR, 'The service you are attempting to delete is currently part of an event.  Please remove the service from the event, or delete the event and then delete the service.')
                return HttpResponseRedirect('/admin/services')

            # Ok, remove it
            else:
                Service.objects.filter(id=id).delete()
                messages.add_message(request, messages.SUCCESS, 'Service successfully removed.')

    # Send them back so they can see the services list again
    return HttpResponseRedirect('/admin/services')


@login_required
@staff_member_required
def service_modify(request):
    """Modify the name of Services
        - This occurs only via AJAX from the services view (it's a POST)

    """

    # If this is a POST, then validate the form and save the data, otherise do nothing
    if request.method == 'POST':
        
        # Check the form elements
        form = ModifyServiceForm(request.POST)

        if form.is_valid():
            pk = form.cleaned_data['pk']
            value = form.cleaned_data['value']

            # Update it
            try:
                Service.objects.filter(id=pk).update(service_name=value)
            except Exception as e:
                return HttpResponseBadRequest('Error saving update')

            return HttpResponse('Value successfully modified')

        else:
            return HttpResponseBadRequest('Invalid request')