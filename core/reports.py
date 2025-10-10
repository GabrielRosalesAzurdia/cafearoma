import csv
import io
from datetime import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch

class ReportGenerator:
    @staticmethod
    def generate_production_csv(production_tasks, product_batches):
        """Genera reporte de producción en formato CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reporte_produccion_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        
        # Encabezados para tareas de producción
        writer.writerow(['REPORTE DE PRODUCCIÓN - CAFÉ AROMA'])
        writer.writerow(['Fecha de generación:', datetime.now().strftime("%Y-%m-%d %H:%M")])
        writer.writerow([])
        
        # Tareas de producción
        writer.writerow(['TAREAS DE PRODUCCIÓN'])
        writer.writerow(['ID', 'Etapa', 'Progreso (%)', 'Cantidad (kg)', 'Unidad', 'Fecha Inicio', 'Estado'])
        
        for task in production_tasks:
            writer.writerow([
                task.id,
                task.get_stage_display(),
                f"{task.progress}%",
                task.planned_kg,
                task.assigned_unit,
                task.created_at.strftime("%Y-%m-%d %H:%M"),
                "COMPLETADA" if task.stage == 'CO' else "EN PROGRESO"
            ])
        
        writer.writerow([])
        
        # Lotes terminados
        writer.writerow(['LOTES TERMINADOS'])
        writer.writerow(['Código', 'Tipo Café', 'Cantidad (kg)', 'Puntuación', 'Fecha Fabricación', 'Fecha Vencimiento'])
        
        for batch in product_batches:
            writer.writerow([
                batch.code,
                batch.get_coffee_type_display(),
                batch.qty_kg,
                batch.cupping_score or "N/A",
                batch.mfg_date,
                batch.expiry_date
            ])
        
        # Estadísticas
        writer.writerow([])
        writer.writerow(['ESTADÍSTICAS'])
        writer.writerow(['Total tareas:', len(production_tasks)])
        writer.writerow(['Tareas completadas:', len([t for t in production_tasks if t.stage == 'CO'])])
        writer.writerow(['Tareas en progreso:', len([t for t in production_tasks if t.stage != 'CO'])])
        writer.writerow(['Total lotes producidos:', len(product_batches)])
        writer.writerow(['Total café producido (kg):', sum(batch.qty_kg for batch in product_batches)])
        
        return response

    @staticmethod
    def generate_production_pdf(production_tasks, product_batches):
        """Genera reporte de producción en formato PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.darkblue
        )
        elements.append(Paragraph('REPORTE DE PRODUCCIÓN - CAFÉ AROMA', title_style))
        elements.append(Paragraph(f'Fecha de generación: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Estadísticas resumen
        stats_style = ParagraphStyle(
            'StatsStyle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        elements.append(Paragraph('RESUMEN ESTADÍSTICO', stats_style))
        
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total tareas', len(production_tasks)],
            ['Tareas completadas', len([t for t in production_tasks if t.stage == 'CO'])],
            ['Tareas en progreso', len([t for t in production_tasks if t.stage != 'CO'])],
            ['Total lotes producidos', len(product_batches)],
            ['Total café producido (kg)', f"{sum(batch.qty_kg for batch in product_batches):.1f}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Tareas de producción
        elements.append(Paragraph('TAREAS DE PRODUCCIÓN', stats_style))
        
        if production_tasks:
            tasks_data = [['ID', 'Etapa', 'Progreso', 'Cantidad', 'Unidad', 'Fecha Inicio', 'Estado']]
            for task in production_tasks:
                tasks_data.append([
                    str(task.id),
                    task.get_stage_display(),
                    f"{task.progress}%",
                    f"{task.planned_kg} kg",
                    task.assigned_unit,
                    task.created_at.strftime("%Y-%m-%d"),
                    "COMPLETADA" if task.stage == 'CO' else "EN PROGRESO"
                ])
            
            tasks_table = Table(tasks_data, colWidths=[0.5*inch, 1*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch])
            tasks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightcyan])
            ]))
            elements.append(tasks_table)
        else:
            elements.append(Paragraph('No hay tareas de producción registradas.', styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # Lotes terminados
        elements.append(Paragraph('LOTES TERMINADOS', stats_style))
        
        if product_batches:
            batches_data = [['Código', 'Tipo', 'Cantidad', 'Puntuación', 'Fecha Fab.', 'Fecha Venc.']]
            for batch in product_batches:
                batches_data.append([
                    batch.code,
                    batch.get_coffee_type_display(),
                    f"{batch.qty_kg} kg",
                    batch.cupping_score or "N/A",
                    batch.mfg_date.strftime("%Y-%m-%d"),
                    batch.expiry_date.strftime("%Y-%m-%d")
                ])
            
            batches_table = Table(batches_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            batches_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgreen])
            ]))
            elements.append(batches_table)
        else:
            elements.append(Paragraph('No hay lotes terminados registrados.', styles['Normal']))
        
        # Generar PDF
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_produccion_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
        
        return response

    @staticmethod
    def generate_inventory_csv(inventory_items, raw_grains):
        """Genera reporte de inventario en formato CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="reporte_inventario_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response)
        
        # Encabezados
        writer.writerow(['REPORTE DE INVENTARIO - CAFÉ AROMA'])
        writer.writerow(['Fecha de generación:', datetime.now().strftime("%Y-%m-%d %H:%M")])
        writer.writerow([])
        
        # Items de inventario
        writer.writerow(['ITEMS DE INVENTARIO'])
        writer.writerow(['SKU', 'Nombre', 'Tipo', 'Stock Actual (kg)', 'Stock Mínimo (kg)', 'Estado'])
        
        low_stock_count = 0
        for item in inventory_items:
            status = "STOCK BAJO" if item.needs_restock() else "OK"
            if item.needs_restock():
                low_stock_count += 1
            writer.writerow([
                item.sku,
                item.name,
                item.get_type_display(),
                item.stock_kg,
                item.min_stock_kg,
                status
            ])
        
        writer.writerow([])
        
        # Materia prima
        writer.writerow(['MATERIA PRIMA (GRANOS VERDES)'])
        writer.writerow(['Lote', 'Proveedor', 'Tipo', 'Origen', 'Cantidad (kg)', 'Fecha Recepción'])
        
        for grain in raw_grains:
            writer.writerow([
                grain.lot_code,
                grain.supplier,
                grain.get_type_display(),
                grain.origin,
                grain.quantity_kg,
                grain.received_at.strftime("%Y-%m-%d %H:%M")
            ])
        
        # Estadísticas
        writer.writerow([])
        writer.writerow(['ESTADÍSTICAS'])
        writer.writerow(['Total items:', len(inventory_items)])
        writer.writerow(['Items con stock bajo:', low_stock_count])
        writer.writerow(['Total materia prima registrada:', len(raw_grains)])
        writer.writerow(['Stock total (kg):', sum(item.stock_kg for item in inventory_items)])
        
        return response