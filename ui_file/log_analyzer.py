            try:
                # PDF rapor oluştur
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Başlık
                story.append(Paragraph(f"Analiz Raporu - {self.analysis_type.currentText()}", styles['Heading1']))
                story.append(Paragraph(f"Oluşturulma Tarihi: {self.current_time_utc}", styles['Normal']))
                story.append(Paragraph(f"Kullanıcı: {self.current_user}", styles['Normal']))
                
                # Analiz sonuçları tablosu
                data = []
                data.append(['Metrik', 'Değer', 'Durum'])  # Başlık satırı
                
                # Sonuçları tabloya ekle
                for row in range(self.results_table.rowCount()):
                    metric = self.results_table.item(row, 0).text()
                    value = self.results_table.item(row, 1).text()
                    status = self.results_table.item(row, 2).text()
                    data.append([metric, value, status])
                
                # Tablo stilini oluştur
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
                
                # Grafiği ekle
                self.figure.savefig('temp_plot.png')
                story.append(Paragraph("<img src='temp_plot.png'/>", styles['Normal']))
                
                # PDF oluştur
                doc.build(story)
                os.remove('temp_plot.png')  # Geçici dosyayı sil
                
                QMessageBox.information(self, "Başarılı", "Rapor oluşturuldu!")
                
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Rapor oluşturulamadı: {str(e)}")

    def save_analysis_results(self):
        if not self.analysis_results:
            QMessageBox.warning(self, "Hata", "Önce analiz yapın!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sonuçları Kaydet",
            f"analiz_sonuclari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Dosyası (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.analysis_results, f, indent=4)
                QMessageBox.information(self, "Başarılı", "Sonuçlar kaydedildi!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Sonuçlar kaydedilemedi: {str(e)}")