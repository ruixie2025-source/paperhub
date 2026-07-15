import { FileText, Pencil, Trash2 } from "lucide-react"
import { Link } from "react-router-dom"

import type { Paper } from "@/api/paper"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type PaperListProps = {
  deletingPaperId: number | null
  isLoading: boolean
  onDeleteRequest: (paper: Paper) => void
  onEdit: (paper: Paper) => void
  onSelectionChange: (paperId: number, checked: boolean) => void
  papers: Paper[]
  selectedPaperIds: number[]
}

function splitKeywords(keywords: string) {
  return keywords
    .split(/[；;，,]/)
    .map((keyword) => keyword.trim())
    .filter(Boolean)
}

function PaperKeywords({ keywords }: { keywords: string }) {
  const items = splitKeywords(keywords)
  if (items.length === 0) {
    return <span className="text-muted-foreground">—</span>
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {items.slice(0, 3).map((keyword) => (
        <Badge key={keyword}>
          {keyword}
        </Badge>
      ))}
      {items.length > 3 ? (
        <Badge className="border bg-background text-muted-foreground">
          +{items.length - 3}
        </Badge>
      ) : null}
    </div>
  )
}

function PaperActions({
  deletingPaperId,
  onDeleteRequest,
  onEdit,
  paper,
}: {
  deletingPaperId: number | null
  onDeleteRequest: (paper: Paper) => void
  onEdit: (paper: Paper) => void
  paper: Paper
}) {
  return (
    <div className="flex items-center justify-end gap-1">
      <Button
        aria-label={`编辑 ${paper.title}`}
        onClick={() => onEdit(paper)}
        size="icon"
        title="编辑论文"
        type="button"
        variant="ghost"
      >
        <Pencil />
      </Button>
      <Button
        aria-label={`删除 ${paper.title}`}
        disabled={deletingPaperId === paper.id}
        onClick={() => onDeleteRequest(paper)}
        size="icon"
        title="删除论文"
        type="button"
        variant="destructive"
      >
        <Trash2 />
      </Button>
    </div>
  )
}

function PaperList({
  deletingPaperId,
  isLoading,
  onDeleteRequest,
  onEdit,
  onSelectionChange,
  papers,
  selectedPaperIds,
}: PaperListProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-10 text-center text-sm text-muted-foreground" role="status">
          正在加载论文...
        </CardContent>
      </Card>
    )
  }

  if (papers.length === 0) {
    return (
      <div className="rounded-lg border border-dashed bg-muted/20 px-6 py-14 text-center">
        <FileText className="mx-auto size-8 text-muted-foreground" />
        <p className="mt-4 text-base font-medium">还没有论文</p>
        <p className="mt-1 text-sm text-muted-foreground">
          导入一篇 PDF，系统会自动解析论文信息并建立索引。
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="space-y-3 md:hidden">
        {papers.map((paper) => (
          <Card key={paper.id}>
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <input
                  aria-label={`选择论文 ${paper.title}`}
                  checked={selectedPaperIds.includes(paper.id)}
                  className="mt-1 size-4 shrink-0 accent-primary"
                  onChange={(event) => onSelectionChange(paper.id, event.target.checked)}
                  type="checkbox"
                />
                <div className="min-w-0 flex-1">
                  <Link
                    className="line-clamp-2 break-words font-semibold leading-6 hover:text-primary"
                    to={`/papers/${paper.id}`}
                  >
                    {paper.title}
                  </Link>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {[paper.authors, paper.journal, paper.year].filter(Boolean).join(" · ") ||
                      "暂无元数据"}
                  </p>
                  <div className="mt-3">
                    <PaperKeywords keywords={paper.keywords} />
                  </div>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between border-t pt-2">
                <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                  <FileText className="size-3.5" />
                  {paper.pdf_path ? "PDF 已就绪" : "暂无 PDF"}
                </span>
                <PaperActions
                  deletingPaperId={deletingPaperId}
                  onDeleteRequest={onDeleteRequest}
                  onEdit={onEdit}
                  paper={paper}
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="hidden overflow-hidden md:block">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">选择</TableHead>
                <TableHead className="w-[38%]">论文</TableHead>
                <TableHead className="w-[24%]">作者与来源</TableHead>
                <TableHead>关键词</TableHead>
                <TableHead className="w-24 text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {papers.map((paper) => (
                <TableRow key={paper.id}>
                  <TableCell>
                    <input
                      aria-label={`选择论文 ${paper.title}`}
                      checked={selectedPaperIds.includes(paper.id)}
                      className="size-4 accent-primary"
                      onChange={(event) => onSelectionChange(paper.id, event.target.checked)}
                      type="checkbox"
                    />
                  </TableCell>
                  <TableCell>
                    <Link
                      className="line-clamp-2 break-words font-semibold leading-5 hover:text-primary"
                      to={`/papers/${paper.id}`}
                    >
                      {paper.title}
                    </Link>
                    <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{paper.pdf_path ? "PDF 已就绪" : "暂无 PDF"}</span>
                      {paper.doi ? <span className="truncate">DOI {paper.doi}</span> : null}
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    <p className="line-clamp-2">
                      {[paper.authors, paper.journal, paper.year].filter(Boolean).join(" · ") ||
                        "暂无元数据"}
                    </p>
                  </TableCell>
                  <TableCell>
                    <PaperKeywords keywords={paper.keywords} />
                  </TableCell>
                  <TableCell>
                    <PaperActions
                      deletingPaperId={deletingPaperId}
                      onDeleteRequest={onDeleteRequest}
                      onEdit={onEdit}
                      paper={paper}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </>
  )
}

export { PaperList }
