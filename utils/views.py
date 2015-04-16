from djangomako.shortcuts import render_to_string

# Create your views here.
def commonheader(request) :
    return render_to_string('common_header.mako', {})


def commonfooter() :
    return render_to_string('common_footer.mako', {})