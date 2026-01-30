import React from 'react';

/**
 * Skeleton loading components for the Chemical Equipment Visualizer
 * Used to show placeholder content while data is loading
 */

// Basic skeleton line (text placeholder)
export const SkeletonLine = ({ width = '100%', height = '14px', style = {} }) => (
    <div
        className="skeleton-line"
        style={{ width, height, ...style }}
    />
);

// Skeleton box (for charts, images, larger areas)
export const SkeletonBox = ({ width = '100%', height = '200px', style = {} }) => (
    <div
        className="skeleton-box"
        style={{ width, height, ...style }}
    />
);

// Skeleton stat card (matches the stats-grid cards)
export const SkeletonStatCard = () => (
    <div className="glass-card skeleton-stat">
        <SkeletonLine width="60%" height="36px" style={{ margin: '0 auto 12px auto' }} />
        <SkeletonLine width="80%" height="12px" style={{ margin: '0 auto' }} />
    </div>
);

// Skeleton history item (matches sidebar history items)
export const SkeletonHistoryItem = () => (
    <div className="skeleton-history-item">
        <SkeletonLine width="50%" height="16px" />
        <SkeletonLine width="70%" height="12px" style={{ marginTop: '8px', marginBottom: 0 }} />
    </div>
);

// Skeleton chart (for chart placeholders)
export const SkeletonChart = ({ height = '300px' }) => (
    <div className="skeleton-chart">
        <SkeletonLine width="40%" height="20px" />
        <SkeletonBox height={height} />
    </div>
);

// Full dashboard skeleton (shows when no data is selected)
export const DashboardSkeleton = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Header skeleton */}
        <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ flex: 1 }}>
                <SkeletonLine width="200px" height="24px" />
                <SkeletonLine width="350px" height="14px" style={{ marginTop: '12px' }} />
            </div>
            <SkeletonBox width="160px" height="40px" />
        </div>

        {/* Stats grid skeleton */}
        <div className="stats-grid">
            <SkeletonStatCard />
            <SkeletonStatCard />
            <SkeletonStatCard />
            <SkeletonStatCard />
        </div>

        {/* Charts grid skeleton */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            <div className="glass-card">
                <SkeletonChart height="250px" />
            </div>
            <div className="glass-card">
                <SkeletonChart height="250px" />
            </div>
        </div>

        {/* Line chart skeleton */}
        <div className="glass-card">
            <SkeletonChart height="280px" />
        </div>

        {/* Table skeleton */}
        <div className="glass-card">
            <SkeletonLine width="180px" height="20px" style={{ marginBottom: '20px' }} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <SkeletonLine width="100%" height="40px" />
                <SkeletonLine width="100%" height="32px" />
                <SkeletonLine width="100%" height="32px" />
                <SkeletonLine width="100%" height="32px" />
                <SkeletonLine width="100%" height="32px" />
            </div>
        </div>
    </div>
);

// History sidebar skeleton
export const HistorySkeleton = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <SkeletonHistoryItem />
        <SkeletonHistoryItem />
        <SkeletonHistoryItem />
    </div>
);

export default {
    SkeletonLine,
    SkeletonBox,
    SkeletonStatCard,
    SkeletonHistoryItem,
    SkeletonChart,
    DashboardSkeleton,
    HistorySkeleton
};
