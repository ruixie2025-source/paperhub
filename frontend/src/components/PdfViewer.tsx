import { useEffect, useRef, useState } from "react"
import { Document, Page, pdfjs } from "react-pdf"
import "react-pdf/dist/Page/AnnotationLayer.css"
import "react-pdf/dist/Page/TextLayer.css"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString()

type PdfViewerProps = {
  fileUrl: string
}

function PdfViewer({ fileUrl }: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null)
  const [pageWidth, setPageWidth] = useState(760)
  const viewerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const viewer = viewerRef.current
    if (!viewer) {
      return
    }

    function updatePageWidth() {
      const currentViewer = viewerRef.current
      if (currentViewer) {
        setPageWidth(Math.max(240, Math.min(760, currentViewer.clientWidth - 16)))
      }
    }

    updatePageWidth()
    const observer = new ResizeObserver(updatePageWidth)
    observer.observe(viewer)
    return () => observer.disconnect()
  }, [])

  return (
    <Card>
      <CardHeader className="border-b">
        <CardTitle>PDF 在线阅读</CardTitle>
        <p className="text-sm text-muted-foreground">
          共 {numPages ?? "—"} 页，可在阅读区域内连续滚动。
        </p>
      </CardHeader>
      <CardContent className="p-3 sm:p-5">
        <div
          className="max-h-[780px] max-w-full overflow-auto rounded-md border bg-muted/30 p-2 sm:p-4"
          ref={viewerRef}
        >
          <Document
            error={
              <p className="text-sm text-destructive">
                PDF 加载失败。你仍然可以使用上方的“打开”按钮查看文件。
              </p>
            }
            file={fileUrl}
            loading={
              <p className="p-4 text-sm text-muted-foreground" role="status">
                正在加载 PDF...
              </p>
            }
            onLoadSuccess={({ numPages: loadedPages }) => setNumPages(loadedPages)}
          >
            <div className="space-y-4">
              {Array.from(new Array(numPages ?? 0), (_page, index) => (
                <Page
                  className="mx-auto max-w-full overflow-hidden rounded-md bg-background shadow-sm [&_canvas]:!h-auto [&_canvas]:!max-w-full"
                  key={`page_${index + 1}`}
                  pageNumber={index + 1}
                  width={pageWidth}
                />
              ))}
            </div>
          </Document>
        </div>
      </CardContent>
    </Card>
  )
}

export { PdfViewer }
