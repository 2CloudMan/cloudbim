from djangomako.shortcuts import render_to_string, render_to_response

# Create your views here.
def commonheader(user) :
    
    return render_to_string('common_header.mako',
                            {'user':user})


def commonfooter() :
    return render_to_string('common_footer.mako', {})



def serve_404_error(request, *args, **kwargs):
  """Registered handler for 404. We just return a simple error"""
  #access_warn(request, "404 not found")
  return render_to_response("404.mako", dict(uri=request.build_absolute_uri()), status=404)

def serve_500_error(request, *args, **kwargs):
  """Registered handler for 500. We use the debug view to make debugging easier."""
  try:
    exc_info = sys.exc_info()
    if exc_info:
      if desktop.conf.HTTP_500_DEBUG_MODE.get() and exc_info[0] and exc_info[1]:
        # If (None, None, None), default server error describing why this failed.
        return django.views.debug.technical_500_response(request, *exc_info)
      else:
        # Could have an empty traceback
        return render("500.mako", request, {'traceback': traceback.extract_tb(exc_info[2])})
    else:
      # exc_info could be empty
      return render("500.mako", request, {})
  finally:
    # Fallback to default 500 response if ours fails
    # Will end up here:
    #   - Middleware or authentication backends problems
    #   - Certain missing imports
    #   - Packaging and install issues
    pass