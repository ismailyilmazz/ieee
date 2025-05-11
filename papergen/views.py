from django.shortcuts import render
from django.http import HttpResponse
from docxtpl import DocxTemplate
import os
import io
from django.conf import settings

def home(request):
    return render(request, 'papergen/home.html')

def generate_doc(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    data = {
        'title': request.POST.get('title'),
        'abstract': request.POST.get('abstract'),
        'conclusion': request.POST.get('conclusion', ''),
        'references': request.POST.getlist('reference'),
        'authors': [],
        'sections': []
        }
    
    names = request.POST.getlist('author_name')
    orgs = request.POST.getlist('author_org')
    locs = request.POST.getlist('author_location')
    emails = request.POST.getlist('author_email')
    for n, o, l, e in zip(names, orgs, locs, emails):
        data['authors'].append({
            'name': n,
            'org': o,
            'location': l,
            'email': e
        })

    section_titles = request.POST.getlist('section_title')
    section_contents = request.POST.getlist('section_content')
    subsection_titles = request.POST.getlist('subsection_title')
    subsection_contents = request.POST.getlist('subsection_content')

    subsections = [{'subtitle': t, 'subcontent': c} for t, c in zip(subsection_titles, subsection_contents)]

    for i, (t, c) in enumerate(zip(section_titles, section_contents)):
        data['sections'].append({
            'title': t,
            'content': c,
            'subsections': subsections  
        })
    
    tpl_path = os.path.join(settings.BASE_DIR, 'papergen','templates', 'papergen', 'ieee_template.docx')
    doc = DocxTemplate(tpl_path)
    doc.render(data)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="ieee_paper.docx"'
    return response

