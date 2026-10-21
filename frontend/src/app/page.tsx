"use client";

import Link from "next/link";
import {
  Sparkles,
  TrendingUp,
  PackageCheck,
  BrainCircuit,
  ArrowRight,
  Database,
  BarChart2,
  ShieldCheck,
  CheckCircle2
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-30 px-6 py-4 flex items-center justify-between max-w-7xl mx-auto w-full">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight text-white">DemandIQ AI</span>
            <span className="hidden sm:inline-block ml-2 text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
              Enterprise v1.0
            </span>
          </div>
        </div>

        <nav className="flex items-center space-x-4">
          <Link
            href="/dashboard"
            className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
          >
            Dashboard
          </Link>
          <Link
            href="/datasets"
            className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
          >
            Datasets
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-500 transition-all shadow-md shadow-blue-600/30"
          >
            <span>Launch Platform</span>
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center items-center text-center px-6 py-20 max-w-5xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Full-Stack Machine Learning & Supply Chain Analytics</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl leading-tight">
          Forecast Smarter. Stock Smarter. <span className="text-blue-500">Grow Better.</span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl leading-relaxed">
          AI-Powered demand forecasting and inventory optimization platform for retail businesses.
          Trained on Walmart M5 and customizable for any retail sales CSV dataset.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center gap-4">
          <Link
            href="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-500 transition-all shadow-lg shadow-blue-600/30 text-base"
          >
            <span>Open Live Dashboard</span>
            <ArrowRight className="w-5 h-5 ml-2" />
          </Link>
          <Link
            href="/datasets"
            className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-xl font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all text-base"
          >
            <Database className="w-5 h-5 mr-2 text-slate-400" />
            <span>Upload Retail CSV</span>
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 text-left w-full">
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 backdrop-blur hover:border-blue-500/50 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center mb-4">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Leakage-Free ML Forecasting</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Compares Naive, Seasonal Naive, Ridge, XGBoost, and LightGBM models using strict chronological
              validation and multi-step recursive horizons.
            </p>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 backdrop-blur hover:border-emerald-500/50 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
              <PackageCheck className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Inventory Optimization Engine</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Calculates safety stock, dynamic reorder points, order-up-to target stock, and suggested
              order quantities under lead time and MOQ constraints.
            </p>
          </div>

          <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-6 backdrop-blur hover:border-purple-500/50 transition-colors">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center mb-4">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Explainable AI (SHAP)</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Provides genuine SHAP feature attributions and demand driver insights so supply chain
              planners can trust algorithmic decisions.
            </p>
          </div>
        </div>

        {/* Verification badges */}
        <div className="mt-12 flex flex-wrap justify-center items-center gap-6 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Walmart M5 Compatible</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Zero Data Fabrication</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>FastAPI & PostgreSQL / SQLite</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>100% Automated Unit & Integration Tests</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        DemandIQ AI &bull; AI-Powered Demand Forecasting &amp; Inventory Optimization
      </footer>
    </div>
  );
}
