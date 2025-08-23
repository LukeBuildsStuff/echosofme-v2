import { Card, CardContent } from "@/components/ui/card"
import { type ReactNode } from "react"

interface StatCardProps {
  name: string
  value: string | number
  growth?: string
  icon?: ReactNode
  trend?: 'up' | 'down' | 'neutral'
}

export default function StatCard({ name, value, growth, icon, trend = 'neutral' }: StatCardProps) {
  const trendColors = {
    up: 'text-green-500',
    down: 'text-red-500',
    neutral: 'text-gray-500'
  }

  return (
    <Card className="bg-gradient-to-br from-white to-gray-50 shadow-lg border-0">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 uppercase tracking-wide">
              {name}
            </p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {value}
            </p>
            {growth && (
              <div className="flex items-center mt-2">
                <span className={`text-sm font-semibold ${trendColors[trend]}`}>
                  {growth}
                </span>
                <span className="text-sm text-gray-500 ml-1">vs last month</span>
              </div>
            )}
          </div>
          {icon && (
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white shadow-lg">
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}