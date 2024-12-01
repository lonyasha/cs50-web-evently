from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from ..forms import TaskForm
from ..models import Event, Task

@login_required
def load_task_form(request, pk=None, task_id=None):
    '''Load the task form for an event or task.'''
    if task_id:
        task = get_object_or_404(Task, id=task_id)
        form = TaskForm(instance=task)
    else:
        event = get_object_or_404(Event, pk=pk)
        form = TaskForm(event=event)

    html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def reload_task_list(request, pk):
    '''Reload the task list for an event.'''
    event = get_object_or_404(Event, pk=pk)
    tasks = event.task_set.all().order_by('-id') 
    
    html = render_to_string('includes/task_list_partial.html', {'tasks': tasks, 'event': event}, request=request)
    return JsonResponse({'html': html})

@login_required
def create_task(request, pk):
    ''''Create a new task for an event.'''
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, event=event)
        if form.is_valid():
            task = form.save(commit=False)
            task.event = event
            task.save()
            return JsonResponse({'success': True})
        else:
            html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'html': html})

    form = TaskForm(event=event)
    html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def edit_task(request, task_id):
    '''Edit an existing task.'''
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
            return JsonResponse({'success': False, 'html': html})

    form = TaskForm(instance=task)
    html = render_to_string('includes/task_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html': html})

@login_required
def toggle_task_completion(request, task_id):
    '''Toggle the completion status of a task.'''
    task = get_object_or_404(Task, id=task_id)
    task.is_completed = not task.is_completed
    task.save()
    
    # Redirect to the referring page
    referer = request.META.get('HTTP_REFERER')  # Get the referring URL
    if referer:
        return redirect(referer)  # Redirect back to where the request came from
    
    # Fallback: Default to event detail if no referer is found
    return redirect('event_detail', pk=task.event.pk)

@login_required
def delete_task(request, task_id):
    '''Delete a task.'''
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        
        task.delete()
        messages.success(request, "Task deleted successfully.")
        return redirect('event_detail', pk=task.event.pk)