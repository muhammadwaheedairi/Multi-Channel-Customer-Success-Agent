"use client"

import { useEffect, useState } from "react"
import { getMetricsSummary, getChannelMetrics } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  Globe, 
  Mail, 
  MessageSquare, 
  Activity, 
  ExternalLink, 
  FileText, 
  HeartPulse,
  TrendingUp,
  Ticket,
  Users,
  CheckCircle2,
  AlertCircle
} from "lucide-react"
import { motion } from "framer-motion"

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const stagger = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

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

  const CHANNEL_ICONS: Record<string, React.ReactNode> = {
    web_form: <Globe className="text-primary" />,
    email: <Mail className="text-primary" />,
    whatsapp: <MessageSquare className="text-primary" />,
  }

  const CHANNEL_COLORS: Record<string, string> = {
    web_form: "bg-blue-500/10",
    email: "bg-purple-500/10",
    whatsapp: "bg-green-500/10",
  }

  if (loading) return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-4">
      <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
      <p className="text-muted-foreground font-medium animate-pulse">Initializing Digital FTE...</p>
    </div>
  )

  return (
    <div className="pt-32 pb-20">
      <div className="container mx-auto px-6">
        <motion.div
          initial="initial"
          animate="animate"
          variants={stagger}
          className="space-y-12"
        >
          {/* Header */}
          <motion.div variants={fadeIn} className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 mb-4">
                <Activity size={14} className="text-primary" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-primary">
                  System Status: Operational
                </span>
              </div>
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">Digital FTE <span className="text-primary italic">Dashboard</span></h1>
              <p className="text-muted-foreground mt-2 text-lg">Real-time performance overview of your autonomous support agent.</p>
            </div>
            <div className="flex items-center gap-3 bg-muted/30 p-2 rounded-2xl border border-border/50">
              <div className="relative flex h-3 w-3 ml-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </div>
              <span className="text-sm font-bold pr-2">AI Agent Live</span>
            </div>
          </motion.div>

          {/* Summary Cards */}
          {summary && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { label: "Total Tickets", value: summary.total_tickets, icon: <Ticket />, color: "text-blue-500", bg: "bg-blue-500/10" },
                { label: "Open Tickets", value: summary.open_tickets, icon: <AlertCircle />, color: "text-orange-500", bg: "bg-orange-500/10" },
                { label: "Resolved", value: summary.resolved_tickets, icon: <CheckCircle2 />, color: "text-green-500", bg: "bg-green-500/10" },
                { label: "Total Customers", value: summary.total_customers, icon: <Users />, color: "text-purple-500", bg: "bg-purple-500/10" },
              ].map((stat, i) => (
                <motion.div key={stat.label} variants={fadeIn}>
                  <Card className="border-none shadow-none bg-muted/30 backdrop-blur-sm hover:bg-muted/50 transition-all group overflow-hidden relative">
                    <div className={`absolute top-0 right-0 w-24 h-24 ${stat.bg} rounded-full translate-x-8 -translate-y-8 blur-2xl opacity-50 group-hover:opacity-100 transition-opacity`} />
                    <CardHeader className="pb-2">
                      <div className={`w-10 h-10 ${stat.bg} ${stat.color} rounded-xl flex items-center justify-center mb-2`}>
                        {stat.icon}
                      </div>
                      <CardTitle className="text-sm text-muted-foreground font-bold uppercase tracking-wider">
                        {stat.label}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-4xl font-black tracking-tighter">{stat.value.toLocaleString()}</p>
                      <div className="flex items-center gap-1 mt-2 text-xs font-bold text-green-500">
                        <TrendingUp size={12} />
                        <span>+12% this week</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}

          {/* Channel Breakdown */}
          <motion.div variants={fadeIn}>
            <Card className="border-none shadow-none bg-muted/10 backdrop-blur-sm overflow-hidden">
              <CardHeader className="border-b border-border/50 bg-muted/20 pb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl font-bold tracking-tight">Channel Performance</CardTitle>
                    <p className="text-sm text-muted-foreground">Detailed breakdown of AI interactions across all platforms (Last 24h)</p>
                  </div>
                  <Badge variant="outline" className="font-bold border-primary/20 text-primary bg-primary/5">
                    Updated just now
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                {Object.keys(channels).length === 0 ? (
                  <div className="py-12 text-center">
                    <p className="text-muted-foreground">No channel data available at this moment.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {Object.entries(channels).map(([channel, data]: [string, any], i) => (
                      <div key={channel} className="relative group">
                        <div className="space-y-6">
                          <div className="flex items-center gap-4">
                            <div className={`w-14 h-14 ${CHANNEL_COLORS[channel] || "bg-primary/10"} rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110 duration-500`}>
                              {CHANNEL_ICONS[channel] || <Activity className="text-primary" />}
                            </div>
                            <div>
                              <p className="text-lg font-bold capitalize tracking-tight">{channel.replace("_", " ")}</p>
                              <div className="flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                                <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Active</span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="space-y-4">
                            {[
                              { label: "Conversations", value: data.total_conversations, sub: "Total handled" },
                              { label: "Escalations", value: data.escalations, sub: "Human required", color: "text-orange-500" },
                              { label: "Avg Sentiment", value: data.avg_sentiment ? `${(data.avg_sentiment * 100).toFixed(0)}%` : "N/A", sub: "Customer satisfaction" },
                            ].map((item) => (
                              <div key={item.label} className="flex justify-between items-end border-b border-border/50 pb-2">
                                <div>
                                  <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground/70">{item.label}</p>
                                  <p className="text-[10px] text-muted-foreground/50">{item.sub}</p>
                                </div>
                                <span className={`text-xl font-black tracking-tighter ${item.color || "text-foreground"}`}>
                                  {item.value}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Quick Actions */}
          <motion.div variants={fadeIn}>
            <div className="bg-primary rounded-[2.5rem] p-8 md:p-12 text-primary-foreground relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl" />
              
              <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="max-w-md text-center md:text-left">
                  <h2 className="text-2xl md:text-3xl font-bold mb-2 tracking-tight">System Controls</h2>
                  <p className="text-primary-foreground/70 text-sm">Access technical documentation, health checks, and manual ticket entry.</p>
                </div>
                
                <div className="flex flex-wrap justify-center gap-4">
                  <a href="/support">
                    <Button variant="secondary" className="h-12 px-6 font-bold shadow-lg">
                      <FileText className="mr-2" size={18} />
                      Submit Ticket
                    </Button>
                  </a>
                  <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" className="h-12 px-6 font-bold bg-transparent border-primary-foreground/30 hover:bg-primary-foreground/10">
                      <ExternalLink className="mr-2" size={18} />
                      API Docs
                    </Button>
                  </a>
                  <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" className="h-12 px-6 font-bold bg-transparent border-primary-foreground/30 hover:bg-primary-foreground/10">
                      <HeartPulse className="mr-2" size={18} />
                      Health Check
                    </Button>
                  </a>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.p variants={fadeIn} className="text-center text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground/50">
            Auto-refreshes every 10 seconds • Digital FTE Factory • SupportIQ v1.0
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}
