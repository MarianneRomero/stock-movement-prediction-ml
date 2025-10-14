import React, { useState, useEffect, useMemo } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ReferenceLine } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Percent, AlertCircle } from 'lucide-react';
import './BacktestDashboard.css';

const BacktestDashboard = () => {

    const [backtestData, setBacktestData] = useState(
        {
            dailyReturns: [],
            stockPerformance: [],
            confidenceAnalysis: [],
            monthlyStats: []
        }
    );

    useEffect(() => {
        const fetchData = async () => {
            try {
                const dailyRes = await fetch("http://localhost:8000/backtest/daily-returns");
                console.log("Daily fetch status:", dailyRes.status);
                const dailyData = await dailyRes.json();
                console.log("Daily data:", dailyData);

                const stockRes = await fetch("http://localhost:8000/backtest/performance-per-stock");
                console.log("Stock fetch status:", stockRes.status);
                const stockData = await stockRes.json();
                console.log("Stock data:", stockData);

                setBacktestData({
                    dailyReturns: Array.isArray(dailyData.portfolioReturns) ? dailyData.portfolioReturns : [],
                    stockPerformance: Array.isArray(stockData.stockPerformance) ? stockData.stockPerformance : [],
                    confidenceAnalysis: [
                        { confidence: '0.5-0.6', accuracy: 0.45, count: 120, avgReturn: 0.002 },
                        { confidence: '0.6-0.7', accuracy: 0.52, count: 95, avgReturn: 0.008 },
                        { confidence: '0.7-0.8', accuracy: 0.58, count: 68, avgReturn: 0.012 },
                        { confidence: '0.8-0.9', accuracy: 0.62, count: 42, avgReturn: 0.018 },
                        { confidence: '0.9-1.0', accuracy: 0.65, count: 25, avgReturn: 0.025 },
                    ],

                    // Monthly breakdown
                    monthlyStats: [
                        { month: 'Jan', longWins: 12, longLosses: 8, shortWins: 5, shortLosses: 7, return: 0.025 },
                        { month: 'Feb', longWins: 10, longLosses: 9, shortWins: 6, shortLosses: 5, return: 0.012 },
                        { month: 'Mar', longWins: 8, longLosses: 11, shortWins: 7, shortLosses: 6, return: -0.008 },
                        { month: 'Apr', longWins: 14, longLosses: 7, shortWins: 8, shortLosses: 4, return: 0.032 },
                        { month: 'May', longWins: 11, longLosses: 10, shortWins: 6, shortLosses: 6, return: 0.015 },
                        { month: 'Jun', longWins: 9, longLosses: 12, shortWins: 5, shortLosses: 8, return: -0.012 },
                    ],
                });
            } catch (err) {
                console.error("Failed to fetch backtest data", err);
            }
        };

        fetchData();
    }, []);


    const [strategy, setStrategy] = useState('long-short');
    const [confidenceThreshold, setConfidenceThreshold] = useState(0.6);

    const [summaryStats, setSummaryStats] = useState(
        {
            totalReturn: 0,
            sharpe: 0,
            winRate: 0,
            maxDrawdown: 0,
            totalTrades: 0
        }
    );

    useEffect(() => {
        const fetchData = async () => {
            try {
                const stats = await fetch("http://localhost:8000/backtest/global-stats");
                const statsData = await stats.json();
                console.log(statsData);
                setSummaryStats(statsData);
            } catch (err) {
                console.error("Failed to fetch backtest data", err);
            }
        };

        fetchData();
    }, []);


    const StatCard = ({ icon: Icon, label, value, subValue, positive }) => (
        <div className="stat-card">
            <div className="stat-card-header">
                <span className="stat-card-label">{label}</span>
                <Icon className={`stat-card-icon ${positive ? 'positive' : positive === false ? 'negative' : 'neutral'}`} />
            </div>
            <div className={`stat-card-value ${positive ? 'positive' : positive === false ? 'negative' : 'neutral'}`}>
                {value}
            </div>
            {subValue && <div className="stat-card-sub">{subValue}</div>}
        </div>
    );

    return (
        <div className="dashboard-container">
            <div className="dashboard-content">
                <div className="header">
                    <h1>Trading Strategy Backtest</h1>
                    <p>Multi-stock portfolio performance analysis</p>
                </div>

                <div className="controls">
                    <div className="control-group">
                        <label>Strategy Type</label>
                        <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                            <option value="long-only">Long Only (Top 20%)</option>
                            <option value="long-short">Long/Short (Top 20% / Bottom 20%)</option>
                            <option value="top-n">Top N Stocks</option>
                        </select>
                    </div>
                    <div className="control-group">
                        <label>Confidence Threshold</label>
                        <input
                            type="range"
                            min="0.5"
                            max="0.9"
                            step="0.05"
                            value={confidenceThreshold}
                            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                        />
                        <span className="threshold-value">{(confidenceThreshold * 100).toFixed(0)}%</span>
                    </div>
                </div>

                {/* Summary Stats */}
                <div className="stats-grid">
                    <StatCard
                        icon={TrendingUp}
                        label="Total Return"
                        value={`${(summaryStats.totalReturn * 100).toFixed(2)}%`}
                        /*subValue={`vs ${(summaryStats.buyHoldReturn * 100).toFixed(2)}% B&H`}*/
                        positive={summaryStats.totalReturn > 0} /*summaryStats.buyHoldReturn}*/
                    />
                    <StatCard
                        icon={Percent}
                        label="Sharpe Ratio"
                        value={summaryStats.sharpe.toFixed(2)}
                        positive={summaryStats.sharpe > 1}
                    />
                    <StatCard
                        icon={DollarSign}
                        label="Win Rate"
                        value={`${(summaryStats.winRate * 100).toFixed(1)}%`}
                        positive={summaryStats.winRate > 0.5}
                    />
                    <StatCard
                        icon={TrendingDown}
                        label="Max Drawdown"
                        value={`${(summaryStats.maxDrawdown * 100).toFixed(2)}%`}
                        positive={false}
                    />
                    <StatCard
                        icon={AlertCircle}
                        label="Total Trades"
                        value={summaryStats.totalTrades}
                    />
                    <StatCard
                        icon={DollarSign}
                        label="Avg Trade"
                        value={`${(summaryStats.avgTrade * 100).toFixed(3)}%`}
                    />
                </div>

                {/* Cumulative Returns by Stock */}
                <div className="chart-container">
                    <h2 className="chart-title">Cumulative Portfolio Returns</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={backtestData.dailyReturns}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="Date" />
                            <YAxis tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                            <Tooltip formatter={(value) => `${(value * 100).toFixed(2)}%`} />
                            <Legend />
                            <Line type="monotone" dataKey="CumulativeReturn" stroke="#10b981" strokeWidth={2} name="Strategy" />
                            <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>


                {/* Stock Performance Table */}
                <div className="chart-container">
                    <h2 className="chart-title">Per-Stock Performance</h2>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Ticker</th>
                                    <th className="text-right">Trades</th>
                                    <th className="text-right">Win Rate</th>
                                    <th className="text-right">Avg Return</th>
                                    <th className="text-right">Sharpe</th>
                                </tr>
                            </thead>
                            <tbody>
                                {backtestData.stockPerformance
                                    .sort((a, b) => b.avgReturn - a.avgReturn)
                                    .map((stock) => (
                                        <tr key={stock.ticker}>
                                            <td className="font-medium">{stock.ticker}</td>
                                            <td className="text-right">{stock.trades}</td>
                                            <td className={`text-right ${stock.winRate > 0.5 ? 'positive' : 'negative'}`}>
                                                {(stock.winRate * 100).toFixed(1)}%
                                            </td>
                                            <td className={`text-right ${stock.avgReturn > 0 ? 'positive' : 'negative'}`}>
                                                {(stock.avgReturn * 100).toFixed(2)}%
                                            </td>
                                            <td className={`text-right ${stock.sharpe > 0 ? 'positive' : 'negative'}`}>
                                                {stock.sharpe.toFixed(2)}
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Confidence vs Accuracy */}
                <div className="chart-container">
                    <h2 className="chart-title">Prediction Confidence Analysis</h2>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={backtestData.confidenceAnalysis}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="confidence" />
                            <YAxis yAxisId="left" tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                            <YAxis yAxisId="right" orientation="right" />
                            <Tooltip />
                            <Legend />
                            <Bar yAxisId="left" dataKey="accuracy" fill="#10b981" name="Accuracy" />
                            <Bar yAxisId="right" dataKey="count" fill="#6366f1" name="Count" />
                            <ReferenceLine yAxisId="left" y={0.5} stroke="#ef4444" strokeDasharray="3 3" />
                        </BarChart>
                    </ResponsiveContainer>
                    <p className="text-xs text-gray-600 mt-2">
                        Higher confidence predictions should have better accuracy. If flat, model may not be calibrated.
                    </p>
                </div>

                {/* Monthly Win/Loss Breakdown */}
                <div className="chart-container">
                    <h2 className="chart-title">Monthly Win/Loss Breakdown</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={backtestData.monthlyStats}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="longWins" stackId="long" fill="#10b981" name="Long Wins" />
                            <Bar dataKey="longLosses" stackId="long" fill="#ef4444" name="Long Losses" />
                            <Bar dataKey="shortWins" stackId="short" fill="#06b6d4" name="Short Wins" />
                            <Bar dataKey="shortLosses" stackId="short" fill="#f97316" name="Short Losses" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Key Insights */}
                <div className="insights-box">
                    <h2 className="insights-title">
                        <AlertCircle className="insights-icon" />
                        Key Insights
                    </h2>
                    <ul className="insights-list">
                        <li>• Strategy {summaryStats.totalReturn > summaryStats.buyHoldReturn ? 'OUTPERFORMS' : 'UNDERPERFORMS'} buy & hold by {Math.abs((summaryStats.totalReturn - summaryStats.buyHoldReturn) * 100).toFixed(2)}%</li>
                        <li>• Sharpe ratio of {summaryStats.sharpe.toFixed(2)} indicates {summaryStats.sharpe > 1 ? 'good' : summaryStats.sharpe > 0.5 ? 'acceptable' : 'poor'} risk-adjusted returns</li>
                        <li>• Win rate of {(summaryStats.winRate * 100).toFixed(1)}% {summaryStats.winRate > 0.55 ? 'is strong' : summaryStats.winRate > 0.5 ? 'is slightly positive' : 'needs improvement'}</li>
                        <li>• Max drawdown of {(Math.abs(summaryStats.maxDrawdown) * 100).toFixed(2)}% shows {Math.abs(summaryStats.maxDrawdown) < 0.15 ? 'low' : Math.abs(summaryStats.maxDrawdown) < 0.25 ? 'moderate' : 'high'} risk exposure</li>
                        <li>
                            • Higher confidence predictions show {
                                (backtestData.confidenceAnalysis[4]?.accuracy ?? 0) > (backtestData.confidenceAnalysis[0]?.accuracy ?? 0)
                                    ? 'better'
                                    : 'similar'
                            } accuracy - model calibration is {
                                (backtestData.confidenceAnalysis[4]?.accuracy ?? 0) > ((backtestData.confidenceAnalysis[0]?.accuracy ?? 0) + 0.1)
                                    ? 'good'
                                    : 'needs work'
                            }
                        </li>
                    </ul>
                </div>
            </div>
        </div >
    );
};

export default BacktestDashboard;