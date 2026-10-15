from rainypdf.engine.pdf import PdfEngine

def compress(snapshot,output):
 before=len(snapshot.data);path=PdfEngine.export(snapshot,output)
 after=path.stat().st_size
 return {'path':str(path),'before':before,'after':after,'saved':before-after}
