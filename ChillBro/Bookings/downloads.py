from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from collections import defaultdict
# libraries for generating pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
# library for generating excel
import xlwt
from datetime import datetime, timedelta
import pytz


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class GeneratePDF(APIView):

    def get(self, request, *args, **kwargs):
        bookings = Bookings.objects.all()

        all_data = {'total_length': len(bookings)}
        booking_details = []
        for booking in bookings:
            data = {
                'booking_id': booking.id,
                'booking_date': booking.booking_date,
                'booking_status': booking.booking_status,
            }
            booking_details.append(data)
        all_data['data'] = booking_details
        pdf = render_to_pdf('pdf.html', all_data)

        # force download
        if pdf:
            response = Response(pdf, content_type='application/pdf')
            filename = "bookings%s.pdf" % (data['booking_id'])
            # content = "inline; filename='%s'" % (filename)
            content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return Response({"message": "Not able to generate PDF", "error": "Not able to generate PDF"}, 400)


class GenerateExcel(APIView):

    def get(self, request, *args, **kwargs):
        response = Response(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=excel_example' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')

        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Booking Id', 'Booking Date', 'Booking Status']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = Bookings.objects.all().values_list('id', 'booking_date', 'booking_status')

        for row in rows:
            row_num += 1

            for col_num in range(3):
                ws.write(row_num, col_num, str(row[col_num]), font_style)

        wb.save(response)
        return response