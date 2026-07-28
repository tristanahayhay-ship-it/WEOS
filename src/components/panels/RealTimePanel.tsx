import { useEffect, useMemo, useState } from 'react'

import { commodities, cryptoPrices, forexRates, orderBook, stockTickers, tradeFeed } from '../../data/mockData'
import type { CommodityRow, ForexRow, OrderBookLevel, TickerRow, TradeFeedItem } from '../../types'

const evolveValue = (base: number, step: number, swing: number) => Number((base + Math.sin(step / 3) * swing).toFixed(2))

export function RealTimePanel() {
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const timer = window.setInterval(() => setTick((value) => value + 1), 1800)
    return () => window.clearInterval(timer)
  }, [])

  const stockRows = useMemo<TickerRow[]>(
    () =>
      stockTickers.map((row, index) => ({
        ...row,
        last: evolveValue(row.last, tick + index, 1.5 + index * 0.3),
        change: evolveValue(row.change, tick + index * 2, 0.35),
      })),
    [tick],
  )

  const forexRows = useMemo<ForexRow[]>(
    () =>
      forexRates.map((row, index) => ({
        ...row,
        rate: evolveValue(row.rate, tick + index, row.pair === 'USD/VND' ? 8 : 0.01),
        change: evolveValue(row.change, tick + index * 2, 0.08),
      })),
    [tick],
  )

  const cryptoRows = useMemo<CommodityRow[]>(
    () =>
      cryptoPrices.map((row, index) => ({
        ...row,
        price: evolveValue(row.price, tick + index, row.symbol === 'BTC' ? 220 : 24),
        change: evolveValue(row.change, tick + index * 3, 0.6),
      })),
    [tick],
  )

  const commodityRows = useMemo<CommodityRow[]>(
    () =>
      commodities.map((row, index) => ({
        ...row,
        price: evolveValue(row.price, tick + index, row.symbol === 'Vàng' ? 4 : 0.45),
        change: evolveValue(row.change, tick + index * 2, 0.2),
      })),
    [tick],
  )

  const tradeRows = useMemo<TradeFeedItem[]>(
    () =>
      tradeFeed.map((row, index) => ({
        ...row,
        notional: `${(parseFloat(row.notional) + (tick % 5) * 0.4 + index * 0.2).toFixed(1)}M USD`,
        timestamp: `00:0${(tick + index) % 6}:${String((tick * 7 + index * 9) % 60).padStart(2, '0')}`,
      })),
    [tick],
  )

  const dynamicOrderBook = useMemo<{ bids: OrderBookLevel[]; asks: OrderBookLevel[] }>(
    () => ({
      bids: orderBook.bids.map((level, index) => ({
        price: evolveValue(level.price, tick + index, 3),
        size: evolveValue(level.size, tick + index, 0.18),
      })),
      asks: orderBook.asks.map((level, index) => ({
        price: evolveValue(level.price, tick + index, 3),
        size: evolveValue(level.size, tick + index, 0.18),
      })),
    }),
    [tick],
  )

  const tables = [
    {
      title: 'Ticker cổ phiếu',
      headers: ['Mã', 'Giá', 'Biến động'] as [string, string, string],
      rows: formatTableRows(stockRows, (row) => row.symbol, (row) => row.last),
    },
    {
      title: 'Ngoại hối',
      headers: ['Cặp', 'Tỷ giá', 'Biến động'] as [string, string, string],
      rows: formatTableRows(forexRows, (row) => row.pair, (row) => row.rate),
    },
    {
      title: 'Crypto',
      headers: ['Mã', 'Giá', 'Biến động'] as [string, string, string],
      rows: formatTableRows(cryptoRows, (row) => row.symbol, (row) => row.price),
    },
    {
      title: 'Hàng hóa',
      headers: ['Mặt hàng', 'Giá', 'Biến động'] as [string, string, string],
      rows: formatTableRows(commodityRows, (row) => row.symbol, (row) => row.price),
    },
  ]

  return (
    <div className="realtime-panel list-stack">
      <div className="entity-header">
        <div>
          <h3 className="realtime-title">L10 · Dòng dữ liệu thời gian thực</h3>
          <p className="muted">Mô phỏng ticker, FX, crypto, hàng hóa, trade tape và order book.</p>
        </div>
        <span className="badge-chip">AUTO {tick}</span>
      </div>

      <div className="realtime-grid">
        {tables.map((table) => (
          <DataTable key={table.title} title={table.title} headers={table.headers} rows={table.rows} />
        ))}
      </div>

      <div className="panel-card">
        <div className="section-title-row">
          <h3>Trade feed mô phỏng</h3>
          <span className="small-tag">Live tape</span>
        </div>
        <div className="trade-stack">
          {tradeRows.map((row) => (
            <div key={row.id} className="trade-row">
              <div>
                <strong>{row.route}</strong>
                <p className="muted">{row.sector}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className={`trend-${row.tone}`}>{row.notional}</div>
                <p className="muted">{row.timestamp}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="panel-card">
        <div className="section-title-row">
          <h3>Order book mô phỏng · BTC</h3>
          <span className="small-tag">Cấp 2</span>
        </div>
        <div className="orderbook-shell">
          <div className="orderbook-stack">
            {dynamicOrderBook.bids.map((level, index) => (
              <div key={`bid-${index}`} className="trade-row">
                <span className="depth-bid">{level.price.toLocaleString('vi-VN')}</span>
                <span>{level.size.toFixed(2)} BTC</span>
              </div>
            ))}
          </div>
          <div className="orderbook-stack">
            {dynamicOrderBook.asks.map((level, index) => (
              <div key={`ask-${index}`} className="trade-row">
                <span className="depth-ask">{level.price.toLocaleString('vi-VN')}</span>
                <span>{level.size.toFixed(2)} BTC</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

interface DataTableProps {
  title: string
  headers: [string, string, string]
  rows: string[][]
}

interface RowWithChange {
  change: number
}

function DataTable({ title, headers, rows }: DataTableProps) {
  return (
    <div className="panel-card">
      <div className="section-title-row">
        <h3>{title}</h3>
        <span className="small-tag">T+0</span>
      </div>
      <div className="table-shell">
        <div className="table-header">
          {headers.map((header) => (
            <span key={header}>{header}</span>
          ))}
        </div>
        {rows.map((row) => (
          <div key={row.join('-')} className="table-row">
            <span>{row[0]}</span>
            <span>{row[1]}</span>
            <span className={row[2].includes('-') ? 'trend-down' : 'trend-up'}>{row[2]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function formatTableRows<T extends RowWithChange>(
  rows: T[],
  label: (row: T) => string,
  price: (row: T) => number,
) {
  return rows.map((row) => [
    label(row),
    price(row).toLocaleString('vi-VN'),
    `${row.change >= 0 ? '+' : ''}${row.change.toFixed(2)}%`,
  ])
}
