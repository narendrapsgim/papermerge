import logging

from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ngettext

from papermerge.core.models import Automate
from papermerge.core.forms import AutomateForm

logger = logging.getLogger(__name__)


@login_required
def automates_view(request):

    if request.method == 'POST':
        selected_action = request.POST.getlist('_selected_action')
        go_action = request.POST['action']

        if go_action == 'delete_selected':
            deleted, row_count = Automate.objects.filter(
                id__in=selected_action
            ).delete()

            if deleted:
                count = row_count['core.Automate']
                msg_sg = "%(count)s Automate was successfully deleted."
                msg_pl = "%(count)s Automates were successfully deleted."
                messages.info(
                    request,
                    ngettext(msg_sg, msg_pl, count) % {'count': count}
                )

    automates = Automate.objects.filter(user=request.user)

    return render(
        request,
        'admin/automates.html',
        {
            'automates': automates,
        }
    )


@login_required
def automate_view(request):

    action_url = reverse('core:automate')

    form = AutomateForm(user=request.user)

    if request.method == 'POST':

        form = AutomateForm(request.POST)
        if form.is_valid():
            automate = Automate.objects.create(
                name=form.cleaned_data['name'],
                match=form.cleaned_data['match'],
                matching_algorithm=form.cleaned_data['matching_algorithm'],
                is_case_sensitive=form.cleaned_data['is_case_sensitive'],
                dst_folder=form.cleaned_data['dst_folder'],
                user=request.user
            )
            if automate:
                automate.save()
                msg = "Automate %(name)s was successfully created."
                messages.info(
                    request,
                    _(msg) % {'name': automate.name}
                )
            return redirect('core:automates')

    return render(
        request,
        'admin/automate.html',
        {
            'form': form,
            'action_url': action_url,
            'title': _('New Automate'),
        }
    )


@login_required
def automate_change_view(request, id):
    """
    Used to edit existing automates
    """
    automate = get_object_or_404(Automate, id=id)
    action_url = reverse('core:automate_change', args=(id,))

    form = AutomateForm(
        request.POST or None, instance=automate
    )

    if request.method == 'POST':
        if form.is_valid():
            automate = form.save()
            if automate:
                automate.save()
            return redirect('core:automates')

    return render(
        request,
        'admin/automate.html',
        {
            'form': form,
            'action_url': action_url,
            'title': _('Edit Automate'),
            'automate': automate
        }
    )
