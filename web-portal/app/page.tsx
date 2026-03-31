"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  MessageSquare,
  Mail,
  Globe,
  Zap,
  Clock,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

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

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/10 selection:text-primary">
      <Header />

      <main>
        {/* Hero Section */}
        <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-full -z-10 opacity-30 pointer-events-none">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px]" />
          </div>

          <div className="container mx-auto px-6">
            <motion.div
              initial="initial"
              animate="animate"
              variants={stagger}
              className="max-w-4xl mx-auto text-center"
            >
              <motion.div
                variants={fadeIn}
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 mb-8"
              >
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className="text-xs font-bold uppercase tracking-wider text-primary">
                  AI Agent Online 24/7
                </span>
              </motion.div>

              <motion.h1
                variants={fadeIn}
                className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 text-foreground"
              >
                Stop Losing Customers
                <br />
                to <span className="text-primary italic">Slow Support</span>
              </motion.h1>

              <motion.p
                variants={fadeIn}
                className="text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed"
              >
                SupportIQ deploys an autonomous AI agent that handles every
                customer inquiry across Email, WhatsApp, and Web — instantly,
                accurately, and at a fraction of the cost of a human team.
              </motion.p>

              <motion.div
                variants={fadeIn}
                className="flex flex-col sm:flex-row gap-4 justify-center items-center"
              >
                <Link href="/support">
                  <Button size="lg" className="h-14 px-8 text-lg font-bold group shadow-xl shadow-primary/20">
                    Try It Now — It's Free
                    <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" size={20} />
                  </Button>
                </Link>
                <Link href="/dashboard">
                  <Button size="lg" variant="outline" className="h-14 px-8 text-lg font-bold">
                    See Live Dashboard
                  </Button>
                </Link>
              </motion.div>

              <motion.div
                variants={fadeIn}
                className="mt-16 flex flex-wrap justify-center gap-8 opacity-50 grayscale hover:grayscale-0 transition-all duration-500"
              >
                {["Stripe", "Shopify", "Notion", "Vercel"].map((brand) => (
                  <span key={brand} className="text-xl font-black tracking-tighter">
                    {brand}
                  </span>
                ))}
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Features Grid */}
        <section id="features" className="py-24 bg-muted/30 relative">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight">
                One AI Agent. Every Channel.
              </h2>
              <p className="text-muted-foreground max-w-xl mx-auto">
                Your customers reach you from different places. SupportIQ meets
                them exactly where they are — and responds in seconds.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: <Globe className="text-primary" />,
                  title: "Web Support Form",
                  desc: "A clean, embeddable support form on your website. Customers submit issues and get instant AI responses with a ticket ID to track progress.",
                  color: "bg-blue-500/10",
                },
                {
                  icon: <Mail className="text-primary" />,
                  title: "Email Support",
                  desc: "Customers email you like normal. SupportIQ reads every email, understands the issue, and sends a professional reply — automatically.",
                  color: "bg-purple-500/10",
                },
                {
                  icon: <MessageSquare className="text-primary" />,
                  title: "WhatsApp Support",
                  desc: "Support on the world's most popular messaging app. Short, conversational replies that feel human — delivered in under 3 seconds.",
                  color: "bg-green-500/10",
                },
              ].map((f, i) => (
                <motion.div
                  key={f.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <Card className="h-full border-none shadow-none bg-background/50 backdrop-blur-sm hover:bg-background transition-colors group">
                    <CardHeader>
                      <div className={`w-12 h-12 ${f.color} rounded-2xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110`}>
                        {f.icon}
                      </div>
                      <CardTitle className="text-xl">{f.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground leading-relaxed">{f.desc}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="solutions" className="py-24 border-y bg-muted/10">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 tracking-tight">
                How SupportIQ Works
              </h2>
              <p className="text-muted-foreground max-w-xl mx-auto">
                From the moment a customer reaches out to a resolved ticket —
                completely handled by AI, no human required.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  title: "Customer Sends a Message",
                  desc: "Via Web Form, Email, or WhatsApp. SupportIQ receives it instantly, identifies the customer, and logs a ticket automatically.",
                  tag: "Step 1 — Intake",
                  color: "bg-blue-500/10",
                },
                {
                  title: "AI Agent Understands & Responds",
                  desc: "The agent searches your knowledge base, checks the customer's history, and crafts a precise, channel-appropriate reply in seconds.",
                  tag: "Step 2 — Resolution",
                  color: "bg-purple-500/10",
                },
                {
                  title: "Escalate When It Matters",
                  desc: "Complex issues, frustrated customers, or billing disputes are automatically flagged and routed to your human team — with full context.",
                  tag: "Step 3 — Escalation",
                  color: "bg-green-500/10",
                },
              ].map((s, i) => (
                <motion.div
                  key={s.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className={`rounded-2xl p-8 ${s.color} border border-border`}
                >
                  <span className="text-xs font-bold uppercase tracking-widest text-primary mb-4 block">
                    {s.tag}
                  </span>
                  <h3 className="text-xl font-bold mb-3">{s.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{s.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section id="stats" className="py-24 border-y">
          <div className="container mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
              {[
                {
                  value: "< 3s",
                  label: "Average Response Time",
                  icon: <Clock className="mx-auto mb-4 text-primary" size={32} />,
                  detail: "Down from 4+ hours industry average",
                },
                {
                  value: "< $1K",
                  label: "Annual Operating Cost",
                  icon: <ShieldCheck className="mx-auto mb-4 text-primary" size={32} />,
                  detail: "vs $75,000/year for a human support agent",
                },
                {
                  value: "24/7/365",
                  label: "Always Available",
                  icon: <Zap className="mx-auto mb-4 text-primary" size={32} />,
                  detail: "No breaks, no sick days, no time zones",
                },
              ].map((s, i) => (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="flex flex-col items-center"
                >
                  {s.icon}
                  <p className="text-5xl font-black tracking-tighter mb-2">{s.value}</p>
                  <p className="text-lg font-bold mb-1">{s.label}</p>
                  <p className="text-sm text-muted-foreground">{s.detail}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 relative overflow-hidden">
          <div className="container mx-auto px-6">
            <div className="bg-primary rounded-[2.5rem] p-12 md:p-24 text-primary-foreground relative overflow-hidden text-center">
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl" />
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/10 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl" />

              <div className="relative z-10 max-w-2xl mx-auto">
                <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">
                  Ready to transform your customer support?
                </h2>
                <p className="text-primary-foreground/80 text-lg mb-10 leading-relaxed">
                  Join businesses that have replaced slow, expensive support
                  with an AI agent that works harder, faster, and never stops.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/support">
                    <Button size="lg" variant="secondary" className="h-14 px-8 text-lg font-bold">
                      Submit a Ticket
                    </Button>
                  </Link>
                  <Link href="/dashboard">
                    <Button
                      size="lg"
                      variant="outline"
                      className="h-14 px-8 text-lg font-bold bg-transparent border-primary-foreground/30 hover:bg-primary-foreground/10"
                    >
                      View Live Dashboard
                    </Button>
                  </Link>
                </div>
                <div className="mt-8 flex items-center justify-center gap-4 text-sm font-medium opacity-80">
                  <span className="flex items-center gap-1">
                    <CheckCircle2 size={16} /> No credit card required
                  </span>
                  <span className="flex items-center gap-1">
                    <CheckCircle2 size={16} /> Live in minutes
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}