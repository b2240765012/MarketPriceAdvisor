import React, { useMemo } from "react";
import "../styles/ribbon.css";

/**
 * Fiyat Şeridi (Price Ribbon) — bu uygulamanin imza gorseli.
 *
 * Taban fiyatin solunda kalan alan "Yasak Bolge" olarak isaretlenir: sistem
 * bu bolgeye ASLA bir oneri koymaz. Bu, "ters enflasyon korumasi" kuralinin
 * gorsel karsiligidir - kullanici tek bakista marjinin nerede korundugunu gorur.
 */
export default function PriceRibbon({ basePrice, currentPrice, marketPrice, recommendedPrice }) {
  const { domainMin, domainMax, floorPct, currentPct, marketPct, recPct } = useMemo(() => {
    const values = [basePrice, currentPrice, marketPrice, recommendedPrice].filter(
      (v) => typeof v === "number"
    );
    const rawMax = Math.max(...values, basePrice);
    const min = basePrice * 0.82;
    const max = rawMax * 1.12;
    const span = max - min || 1;

    const toPct = (v) => (typeof v !== "number" ? null : Math.min(100, Math.max(0, ((v - min) / span) * 100)));

    return {
      domainMin: min,
      domainMax: max,
      floorPct: toPct(basePrice),
      currentPct: toPct(currentPrice),
      marketPct: toPct(marketPrice),
      recPct: toPct(recommendedPrice),
    };
  }, [basePrice, currentPrice, marketPrice, recommendedPrice]);

  return (
    <div className="ribbon">
      <div className="ribbon-track">
        <div className="ribbon-zone-forbidden" style={{ width: `${floorPct}%` }} />
        <div className="ribbon-zone-safe" style={{ left: `${floorPct}%`, width: `${100 - floorPct}%` }} />

        <div className="ribbon-floor-line" style={{ left: `${floorPct}%` }} title={`Taban Fiyat: ${basePrice.toFixed(2)} TL`} />

        {recPct != null && currentPct != null && recPct > currentPct && (
          <div
            className="ribbon-gap"
            style={{ left: `${currentPct}%`, width: `${recPct - currentPct}%` }}
          />
        )}

        {marketPct != null && (
          <div className="ribbon-marker ribbon-marker-market" style={{ left: `${marketPct}%` }}>
            <span className="ribbon-marker-dot" />
          </div>
        )}

        {currentPct != null && (
          <div className="ribbon-marker ribbon-marker-current" style={{ left: `${currentPct}%` }}>
            <span className="ribbon-marker-dot" />
          </div>
        )}
      </div>

      <div className="ribbon-legend">
        <span className="ribbon-legend-item">
          <i className="ribbon-swatch swatch-floor" /> Taban <b className="mono">{basePrice.toFixed(2)}</b>
        </span>
        <span className="ribbon-legend-item">
          <i className="ribbon-swatch swatch-current" /> Mevcut <b className="mono">{currentPrice.toFixed(2)}</b>
        </span>
        <span className="ribbon-legend-item">
          <i className="ribbon-swatch swatch-market" /> Piyasa{" "}
          <b className="mono">{typeof marketPrice === "number" ? marketPrice.toFixed(2) : "—"}</b>
        </span>
      </div>
    </div>
  );
}
