[⬅ Back to ToC](../README.md)

# 1a. Django views and forms

Let's look at this real life example ([django-registration](https://github.com/ubernostrum/django-registration/) two step flow).

```python
class RegistrationView(FormView):
    """
    Base class for user registration views.
    """
    disallowed_url = reverse_lazy('django_registration_disallowed')
    form_class = RegistrationForm
    success_url = None
    template_name = 'django_registration/registration_form.html'

    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        """
        if not self.registration_allowed():
            return HttpResponseRedirect(force_text(self.disallowed_url))
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    def get_success_url(self, user=None):
        """
        Return the URL to redirect to after successful redirection.
        """
        # This is overridden solely to allow django-registration to
        # support passing the user account as an argument; otherwise,
        # the base FormMixin implementation, which accepts no
        # arguments, could be called and end up raising a TypeError.
        return super(RegistrationView, self).get_success_url()

    def form_valid(self, form):
        return HttpResponseRedirect(
            self.get_success_url(self.register(form))
        )

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def register(self, form):
        """
        Implement user-registration logic here. Access to both the
        request and the registration form is available here.
        """
        raise NotImplementedError
        
        
class RegistrationView(BaseRegistrationView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.
    This is different from the model-based activation workflow in that
    the activation key is the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.
    """
    email_body_template = 'django_registration/activation_email_body.txt'
    email_subject_template = 'django_registration/activation_email_subject.txt'
    success_url = reverse_lazy('django_registration_complete')

    def register(self, form):
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        return new_user

    def create_inactive_user(self, form):
        """
        Create the inactive user account and send an email containing
        activation instructions.
        """
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return signing.dumps(
            obj=user.get_username(),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.
        """
        scheme = 'https' if self.request.is_secure() else 'http'
        return {
            'scheme': scheme,
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is the username,
        signed using TimestampSigner.
        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context['user'] = user
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request
        )
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request
        )
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
```

##### Django Forms
[TODO]

```python
class InitialSignupForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=255, widget=forms.PasswordInput)
    password_repeat = forms.CharField(max_length=255, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean(self):
        form_data = self.cleaned_data
        if form_data['password'] != form_data['password_repeat']:
            self._errors["password"] = ["Password do not match"]
            del form_data['password']
        return form_data
```

### Stating the problem

One can discover 3 problems here:

##### 1. Form is both a data description object & data validation object.
##### 2. Form is both a data description and a presenter (HTML renderer).
##### 3. Business logic is closely coupled with framework views.
