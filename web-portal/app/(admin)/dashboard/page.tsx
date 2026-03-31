"use client"

import { useEffect, useState } from "react"
import { getMetricsSummary, getChannelMetrics } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [channels, setChannels] = useState<any>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [s, c] = await Promise.all([getMetricsSummary(), getChannelMetrics()])
        setSummary(s)
        setChannels(c)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const CHANNEL_ICONS: Record<string, string> = {
    web_form: "🌐",
    email: "📧",
    whatsapp: "💬",
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground">Loading dashboard...</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">FTE Dashboard</h1>
            <p className="text-muted-foreground">Customer Success AI Agent — Live Overview</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <Badge variant="outline">AI Agent Live</Badge>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Total Tickets", value: summary.total_tickets, color: "text-blue-600" },
              { label: "Open Tickets", value: summary.open_tickets, color: "text-yellow-600" },
              { label: "Resolved", value: summary.resolved_tickets, color: "text-green-600" },
              { label: "Customers", value: summary.total_customers, color: "text-purple-600" },
            ].map((stat) => (
              <Card key={stat.label}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm text-muted-foreground font-normal">
                    {stat.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Channel Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Channel Performance (Last 24h)</CardTitle>
          </CardHeader>
          <CardContent>
            {Object.keys(channels).length === 0 ? (
              <p className="text-muted-foreground text-sm">No channel data yet.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(channels).map(([channel, data]: [string, any]) => (
                  <div key={channel} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{CHANNEL_ICONS[channel] || "📡"}</span>
                      <div>
                        <p className="font-semibold capitalize">{channel.replace("_", " ")}</p>
                        <Badge variant="secondary" className="text-xs">Active</Badge>
                      </div>
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Conversations</span>
                        <span className="font-medium">{data.total_conversations}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Escalations</span>
                        <span className="font-medium text-red-500">{data.escalations}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Avg Sentiment</span>
                        <span className="font-medium">
                          {data.avg_sentiment ? data.avg_sentiment.toFixed(2) : "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <a href="/support"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:opacity-90">
              📝 Submit Ticket
            </a>
            <a href="http://localhost:8000/docs" target="_blank"
              className="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-muted">
              🔌 API Docs
            </a>
            <a href="http://localhost:8000/health" target="_blank"
              className="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-muted">
              💚 Health Check
            </a>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          Auto-refreshes every 10 seconds • Digital FTE Factory
        </p>
      </div>
    </div>
  )
}
