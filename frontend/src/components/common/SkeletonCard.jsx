import { motion } from 'framer-motion';

// Skeleton Card for Product Loading
export const SkeletonCard = () => (
    <div className="card animate-pulse">
        <div className="aspect-square bg-gray-200"></div>
        <div className="p-5 space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
    </div>
);

// Skeleton for Stats Card
export const SkeletonStat = () => (
    <div className="glass rounded-xl p-4 animate-pulse">
        <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-200 rounded-lg"></div>
            <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded w-12"></div>
                <div className="h-5 bg-gray-200 rounded w-8"></div>
            </div>
        </div>
    </div>
);

// Skeleton for Product Detail Image
export const SkeletonProductImage = () => (
    <div className="card overflow-hidden aspect-square bg-gray-200 animate-pulse"></div>
);

// Skeleton for Product Detail Info
export const SkeletonProductInfo = () => (
    <div className="flex flex-col animate-pulse space-y-4">
        <div className="h-6 bg-gray-200 rounded w-24"></div>
        <div className="h-10 bg-gray-200 rounded w-3/4"></div>
        <div className="flex gap-2">
            <div className="h-5 bg-gray-200 rounded w-24"></div>
            <div className="h-5 bg-gray-200 rounded w-16"></div>
        </div>
        <div className="h-12 bg-gray-200 rounded w-32"></div>
        <div className="space-y-2 mt-4">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
    </div>
);

// Grid of skeleton cards
export const SkeletonGrid = ({ count = 10, cols = 5 }) => (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-${cols} gap-6`}>
        {[...Array(count)].map((_, i) => (
            <SkeletonCard key={i} />
        ))}
    </div>
);

export default SkeletonCard;
