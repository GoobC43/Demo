export const formatCurrency = (value: number | undefined | null) => {
    if (value === undefined || value === null) return "$0";

    // Condense large numbers
    if (value >= 1_000_000) {
        return `$${(value / 1_000_000).toFixed(1)}M`;
    } else if (value >= 1_000) {
        return `$${(value / 1_000).toFixed(1)}K`;
    }

    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
};

export const formatPercentage = (value: number | undefined | null) => {
    if (value === undefined || value === null) return "0%";
    return `${(value * 100).toFixed(0)}%`;
};

export const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "";
    return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
};
