"""Ensure extraction keeps body geometry and remaps local/cross-chapter links."""
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
import pymupdf
from export_chapters import assemble, destination_for, validate, filename

class ChapterExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        book=pymupdf.open()
        for n in range(7):
            page=book.new_page(width=176/25.4*72,height=250/25.4*72);page.insert_text((60,80),f'Full book page {n+1}',fontsize=10);page.draw_line((60,90),(240,90))
        book[2].insert_link({'kind':pymupdf.LINK_GOTO,'from':pymupdf.Rect(60,70,90,80),'page':3,'to':pymupdf.Point(60,100)})
        book[2].insert_link({'kind':pymupdf.LINK_GOTO,'from':pymupdf.Rect(100,70,140,80),'page':4,'to':pymupdf.Point(60,100)})
        book[3].insert_link({'kind':pymupdf.LINK_URI,'from':pymupdf.Rect(60,70,90,80),'uri':'https://example.org/'})
        book.set_toc([[1,'Chapter 1',3],[2,'Section',4],[1,'Chapter 2',5]])
        self.book=pymupdf.open(stream=book.tobytes(),filetype='pdf');self.addCleanup(self.book.close);book.close()
        self.timestamp='2026-10-03 07:00:00 UTC';self.covers=pymupdf.open();self.addCleanup(self.covers.close)
        for n in range(2):self.covers.new_page(width=176/25.4*72,height=250/25.4*72).insert_text((60,80),self.timestamp)
        self.parts=[{'key':'chapter-01','title':'First','first':3,'last':4,'filename':filename('chapter-01')},{'key':'chapter-02','title':'Second','first':5,'last':7,'filename':filename('chapter-02')}]
    def test_local_remote_and_url_links_keep_targets(self):
        p=self.parts[0];doc,_=assemble(self.book,self.covers,p,self.parts,self.timestamp);out=Path(self.temp.name)/p['filename'];doc.save(out,no_new_id=True);doc.close();r=validate(out,self.book,p,self.parts,self.timestamp)
        self.assertEqual((r['internal_links'],r['cross_file_links'],r['web_links']),(1,1,1));self.assertEqual(r['pages'],4);self.assertEqual(r['trailing_blank_pages'],0)
    def test_odd_source_tail_gets_blank_verso(self):
        p=self.parts[1];doc,padded=assemble(self.book,self.covers,p,self.parts,self.timestamp);out=Path(self.temp.name)/p['filename'];doc.save(out,no_new_id=True);doc.close();r=validate(out,self.book,p,self.parts,self.timestamp)
        self.assertTrue(padded);self.assertEqual(r['pages'],6);self.assertEqual(r['trailing_blank_pages'],1)
    def test_inserted_contents_keep_original_folios_and_shift_links(self):
        first,second=self.parts
        first.update(body_start=4,contents_pages=1,contents_blank_pages=1,
            contents_rows=[dict(index=0,level=1,page=3,to=[60,80])],
            contents_destinations={'1':dict(index=0,level=1,page=3,to=[60,80])})
        second.update(body_start=6)
        toc=pymupdf.open()
        for _ in range(2):toc.new_page(width=self.book[0].rect.width,height=self.book[0].rect.height)
        toc[0].insert_text((60,80),'Chapter 1 ........ 3')
        toc[0].insert_link({'kind':pymupdf.LINK_GOTO,'from':pymupdf.Rect(60,70,200,80),'page':1,'to':pymupdf.Point(60,80)})
        contents=pymupdf.open(stream=toc.tobytes(),filetype='pdf');self.addCleanup(contents.close);toc.close()
        doc,_=assemble(self.book,self.covers,first,self.parts,self.timestamp,contents)
        out=Path(self.temp.name)/first['filename'];doc.save(out,no_new_id=True);doc.close()
        r=validate(out,self.book,first,self.parts,self.timestamp)
        self.assertEqual(r['body_first_pdf_page'],5)
        self.assertEqual(r['contents_entries'],1)
        with pymupdf.open(out) as result:
            self.assertEqual(result[2].get_links()[0]['page'],4)
            self.assertEqual(result[4].get_links()[1]['page'],6)
            self.assertEqual(result[4].get_label(),'3')

    def test_covers_and_remote_targets_are_explicit(self):
        self.assertEqual(destination_for(0,self.parts[0],self.parts),{'kind':pymupdf.LINK_GOTO,'page':0})
        self.assertEqual(destination_for(4,self.parts[0],self.parts),{'kind':pymupdf.LINK_GOTOR,'page':2,'file':filename('chapter-02')})

if __name__=='__main__':unittest.main()
