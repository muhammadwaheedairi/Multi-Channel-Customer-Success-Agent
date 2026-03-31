"use client";

import { Button } from "@/components/ui/button";
import { Zap, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import Link from "next/link";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <nav
        className={`fixed top-0 w-full z-50 transition-all duration-300 border-b ${
          scrolled
            ? "bg-background/80 backdrop-blur-md py-3"
            : "bg-transparent py-5 border-transparent"
        }`}
      >
        <div className="container mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2 group cursor-pointer">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-primary-foreground transition-transform group-hover:rotate-12">
              <Zap size={20} fill="currentColor" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold tracking-tight leading-none">
                SupportIQ
              </span>
              <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">
                AI Customer Success
              </span>
            </div>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-medium hover:text-primary transition-colors">
              Features
            </a>
            <a href="#solutions" className="text-sm font-medium hover:text-primary transition-colors">
              How It Works
            </a>
            <a href="#stats" className="text-sm font-medium hover:text-primary transition-colors">
              Results
            </a>
            <div className="h-4 w-[1px] bg-border mx-2" />
            <div className="flex gap-3">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm" className="font-semibold">
                  Dashboard
                </Button>
              </Link>
              <Link href="/support">
                <Button size="sm" className="font-semibold shadow-lg shadow-primary/20">
                  Get Support
                </Button>
              </Link>
            </div>
          </div>

          {/* Mobile Toggle */}
          <button
            className="md:hidden p-2 hover:bg-muted rounded-lg transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-40 bg-background pt-24 px-6 md:hidden"
          >
            <div className="flex flex-col gap-6 text-center">
              <a href="#features" onClick={() => setIsMenuOpen(false)} className="text-2xl font-bold">Features</a>
              <a href="#solutions" onClick={() => setIsMenuOpen(false)} className="text-2xl font-bold">How It Works</a>
              <a href="#stats" onClick={() => setIsMenuOpen(false)} className="text-2xl font-bold">Results</a>
              <div className="flex flex-col gap-3 mt-6">
                <Link href="/dashboard" className="w-full">
                  <Button variant="outline" size="lg" className="w-full">Dashboard</Button>
                </Link>
                <Link href="/support" className="w-full">
                  <Button size="lg" className="w-full">Get Support</Button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}