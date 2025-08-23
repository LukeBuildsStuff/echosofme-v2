import { type ReactNode } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface GradientCardProps {
  title: string
  description?: string
  children: ReactNode
  gradient?: string
  className?: string
}

export default function GradientCard({ 
  title, 
  description, 
  children, 
  gradient = "from-indigo-500 via-purple-500 to-pink-500",
  className = ""
}: GradientCardProps) {
  return (
    <Card className={`bg-gradient-to-br ${gradient} text-white shadow-2xl border-0 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-xl font-bold text-white">{title}</CardTitle>
        {description && (
          <p className="text-white/80 text-sm">{description}</p>
        )}
      </CardHeader>
      <CardContent>
        {children}
      </CardContent>
    </Card>
  )
}