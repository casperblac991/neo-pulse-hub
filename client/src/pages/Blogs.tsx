import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, ChevronDown, Loader2 } from "lucide-react";
import { useState, useMemo } from "react";
import { Streamdown } from "streamdown";

export default function Blogs() {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<"EN" | "AR" | null>(null);

  const blogsQuery = trpc.blogs.all.useQuery();
  const blogs = blogsQuery.data || [];

  const filteredBlogs = useMemo(() => {
    return blogs.filter(blog => !selectedLanguage || blog.language === selectedLanguage);
  }, [blogs, selectedLanguage]);

  const enCount = blogs.filter(b => b.language === "EN").length;
  const arCount = blogs.filter(b => b.language === "AR").length;

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur">
        <div className="container py-6">
          <h1 className="text-3xl font-bold text-gradient">Blog Posts Library</h1>
          <p className="text-sm text-muted-foreground mt-1">View all AI-generated blog content</p>
        </div>
      </div>

      {/* Content */}
      <div className="container py-8 space-y-6">
        {/* Language Filter */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={selectedLanguage === null ? "default" : "outline"}
            onClick={() => setSelectedLanguage(null)}
            className="text-xs"
          >
            All Languages ({blogs.length})
          </Button>
          <Button
            variant={selectedLanguage === "EN" ? "default" : "outline"}
            onClick={() => setSelectedLanguage("EN")}
            className="text-xs"
          >
            EN ({enCount})
          </Button>
          <Button
            variant={selectedLanguage === "AR" ? "default" : "outline"}
            onClick={() => setSelectedLanguage("AR")}
            className="text-xs"
          >
            AR ({arCount})
          </Button>
        </div>

        {/* Blog List */}
        {blogsQuery.isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-primary w-8 h-8" />
          </div>
        ) : filteredBlogs.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No blog posts found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredBlogs.map(blog => (
              <Card
                key={blog.id}
                className="bg-card border-primary/20 hover:border-primary/50 transition-all cursor-pointer"
                onClick={() => setExpandedId(expandedId === blog.id ? null : blog.id)}
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-4 h-4 text-primary" />
                        <h3 className="font-semibold text-foreground text-lg">{blog.title}</h3>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Badge className="bg-accent/20 text-accent border-accent/30">
                          {blog.language}
                        </Badge>
                        {blog.productId && (
                          <Badge className="bg-secondary/20 text-secondary border-secondary/30">
                            Product: {blog.productId}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        Created: {new Date(blog.createdAt).toLocaleString()}
                      </p>
                    </div>
                    <ChevronDown
                      className={`w-5 h-5 text-primary transition-transform ${
                        expandedId === blog.id ? "rotate-180" : ""
                      }`}
                    />
                  </div>

                  {/* Expanded Content */}
                  {expandedId === blog.id && blog.content && (
                    <div className="mt-4 pt-4 border-t border-border">
                      <div className="prose prose-invert max-w-none text-sm">
                        <Streamdown>{blog.content.substring(0, 500) + "..."}</Streamdown>
                      </div>
                      <Button
                        size="sm"
                        className="mt-4 bg-primary/20 hover:bg-primary/40 text-primary border border-primary/50"
                      >
                        Read Full Post
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
