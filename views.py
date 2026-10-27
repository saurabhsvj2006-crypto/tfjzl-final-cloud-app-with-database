from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Course, Enrollment, Submission


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-total_enrollment')[:10]


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'


def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            submitted_answers.append(int(request.POST[key]))
    return submitted_answers


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.get(user=request.user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(extract_answers(request))
    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result',
                args=(course.id, submission.id)))


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = [choice.id for choice in submission.choices.all()]

    total_score = 0
    max_score = 0
    for question in course.question_set.all():
        max_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    grade = int(total_score / max_score * 100) if max_score else 0

    context = {
        'course': course,
        'selected_ids': selected_ids,
        'grade': grade,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
