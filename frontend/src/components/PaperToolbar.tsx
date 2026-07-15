import { RefreshCw, Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type PaperToolbarProps = {
  count: number
  isLoading: boolean
  keyword: string
  onRefresh: () => void
  onSearchChange: (keyword: string) => void
}

function PaperToolbar({
  count,
  isLoading,
  keyword,
  onRefresh,
  onSearchChange,
}: PaperToolbarProps) {
  return (
    <div className="flex flex-col gap-3 border-b pb-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-medium">全部论文</p>
        <p className="mt-0.5 text-sm text-muted-foreground">当前共 {count} 篇</p>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative min-w-0 flex-1 sm:w-80 sm:flex-none">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            aria-label="搜索论文"
            className="pl-9"
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="搜索标题、作者、期刊、关键词"
            value={keyword}
          />
        </div>
        <Button
          aria-label={isLoading ? "正在刷新" : "刷新论文列表"}
          disabled={isLoading}
          onClick={onRefresh}
          size="icon"
          title="刷新论文列表"
          type="button"
          variant="outline"
        >
          <RefreshCw className={isLoading ? "animate-spin" : ""} />
        </Button>
      </div>
    </div>
  )
}

export { PaperToolbar }
