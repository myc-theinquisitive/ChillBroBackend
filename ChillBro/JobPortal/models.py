from django.db import models
import uuid
from .constants import JobType, Cities, States, Countries, JobCategory, JobApplicationStatus
from .validations import is_json
from .helpers import get_user_model


def get_id():
    return str(uuid.uuid4())


class Job(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id, verbose_name="Job Id")
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()

    basic_qualifications = models.TextField(validators=[is_json])
    preferred_qualifications = models.TextField(validators=[is_json])

    job_type = models.CharField(
        max_length=30, choices=[(job_type.value, job_type.value) for job_type in JobType],
        default=JobType.FULL_TIME.value)
    job_category = models.CharField(max_length=50, default=JobCategory.SOFTWARE_DEVELOPMENT.value, choices=
        [(job_category.value, job_category.value) for job_category in JobCategory], verbose_name="Job Category")

    city = models.CharField(max_length=30, default=Cities.VSKP.value,
                            choices=[(city.value, city.value) for city in Cities], verbose_name="City")
    state = models.CharField(max_length=30, default=States.AP.value,
                             choices=[(state.value, state.value) for state in States], verbose_name="State")
    country = models.CharField(max_length=30, default=Countries.IND.value, choices=
        [(country.value, country.value) for country in Countries], verbose_name="Country")

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class JobApplicationsManager(models.Manager):

    def active(self):
        return self.filter(is_withdrawn=False)


class JobApplications(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id, verbose_name="Job Application Id")
    job = models.ForeignKey("Job", on_delete=models.CASCADE, verbose_name="Job")
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="Applied by")
    is_withdrawn = models.BooleanField(default=False, verbose_name="Is withdrawn")
    applied_on = models.DateTimeField(auto_now_add=True)
    application_status = models.CharField(
        max_length=50, default=JobApplicationStatus.YET_TO_VIEW.value, choices=
        [(application_status.value, application_status.value) for application_status in JobApplicationStatus],
        verbose_name="Application Status")

    objects = JobApplicationsManager()

    class Meta:
        unique_together = ('job', 'created_by')
