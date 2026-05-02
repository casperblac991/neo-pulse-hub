import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, ExternalLink, Loader2 } from "lucide-react";
import { useState, useMemo } from "react";

export default function Products() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const productsQuery = trpc.products.all.useQuery();
  const products = productsQuery.data || [];

  const categories = useMemo(() => {
    const cats = new Set(products.map(p => p.category).filter(Boolean));
    return Array.from(cats);
  }, [products]);

  const filteredProducts = useMemo(() => {
    return products.filter(p => {
      const matchesSearch = p.title.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = !selectedCategory || p.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [products, searchTerm, selectedCategory]);

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur">
        <div className="container py-6">
          <h1 className="text-3xl font-bold text-gradient">Products Catalog</h1>
          <p className="text-sm text-muted-foreground mt-1">Manage and view all fetched products</p>
        </div>
      </div>

      {/* Content */}
      <div className="container py-8 space-y-6">
        {/* Search and Filter */}
        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 input-neon"
            />
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedCategory === null ? "default" : "outline"}
              onClick={() => setSelectedCategory(null)}
              className="text-xs"
            >
              All Categories
            </Button>
            {categories.map(cat => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? "default" : "outline"}
                onClick={() => setSelectedCategory(cat)}
                className="text-xs"
              >
                {cat}
              </Button>
            ))}
          </div>
        </div>

        {/* Products Grid */}
        {productsQuery.isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-primary w-8 h-8" />
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No products found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProducts.map(product => (
              <Card key={product.id} className="bg-card border-primary/20 hover:border-primary/50 transition-all p-4">
                {product.image && (
                  <img
                    src={product.image}
                    alt={product.title}
                    className="w-full h-40 object-cover rounded-lg mb-4"
                  />
                )}
                <h3 className="font-semibold text-foreground line-clamp-2">{product.title}</h3>
                
                <div className="flex items-center justify-between mt-3">
                  {product.rating && (
                    <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                      ⭐ {product.rating}
                    </Badge>
                  )}
                  {product.price && (
                    <span className="text-lg font-bold text-primary">${product.price}</span>
                  )}
                </div>

                {product.category && (
                  <Badge className="mt-3 bg-primary/20 text-primary border-primary/30">
                    {product.category}
                  </Badge>
                )}

                {product.reviews && (
                  <p className="text-xs text-muted-foreground mt-2">
                    {product.reviews} reviews
                  </p>
                )}

                {product.url && (
                  <Button
                    size="sm"
                    className="w-full mt-4 bg-secondary/20 hover:bg-secondary/40 text-secondary border border-secondary/50"
                    asChild
                  >
                    <a href={product.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center gap-2">
                      View on Amazon
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </Button>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
