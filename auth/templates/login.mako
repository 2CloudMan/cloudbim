<%!
from utils.views import commonheader, commonfooter
%>

${ commonheader(user) | n,unicode }

<style type="text/css">

.form-signin {
    width: 370px;
    margin: 20px auto 20px;
    padding: 20px;
    background-color:#FFF;
}

</style>

  <div class="container">

      <form class="form-signin" method="POST" action="${action}" class="well">
        ${ csrf_token(request) | n,unicode }
        %if first_login_ever:
          <h3>${_('Create your CloubBIM account')}</h3>
        %else:
          <h3>${_('Sign in to continue to CloubBIM')}</h3>
        %endif

        %if first_login_ever:
          <div class="alert alert-block">
            ${_('Since this is your first time logging in, pick any username and password. Be sure to remember these, as')}
            <strong>${_('they will become your Hue superuser credentials.')}</strong>
            % if is_password_policy_enabled():
	      <p>${get_password_hint()}</p>
            % endif
          </div>
        %endif

        <div class="input-prepend
          % if backend_name == 'OAuthBackend':
            hide
          % endif
        ">
          <span class="add-on"><i class="fa fa-user"></i></span>
          ${ form['username'] | n,unicode }
        </div>

        ${ form['username'].errors | n,unicode }

        <div class="input-prepend
          % if backend_name in ('AllowAllBackend', 'OAuthBackend'):
            hide
          % endif
        ">
          <span class="add-on"><i class="fa fa-lock"></i></span>
          ${ form['password'] | n,unicode }
        </div>
        ${ form['password'].errors | n,unicode }

        %if active_directory:
        <div class="input-prepend">
          <span class="add-on"><i class="fa fa-globe"></i></span>
          ${ form['server'] | n,unicode }
        </div>
        %endif

        %if login_errors and not form['username'].errors and not form['password'].errors:
          <div class="alert alert-error" style="text-align: center">
            <strong><i class="fa fa-exclamation-triangle"></i> ${_('Error!')}</strong>
            % if form.errors:
              % for error in form.errors:
               ${ form.errors[error]|unicode,n }
              % endfor
            % endif
          </div>
        %endif
        <hr/>
        %if first_login_ever:
          <input type="submit" class="btn btn-primary" value="${_('Create account')}"/>
        %else:
          <input type="submit" class="btn btn-primary" value="${_('Sign in')}"/>
        %endif
        <input type="hidden" name="next" value="${next}"/>
      </form>
  </div>
</body>
</html>