"use client"

import Link from 'next/link';
import { useState } from 'react';

import waterCodes from "@/content/WaterCodes.json"

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [showAll, setShowAll] = useState(false);

  const filteredWaterCodes = searchTerm
    ? waterCodes.filter((item) => {
        const dayNumber = item.Tweet.match(/Day (\d+) of ML:/);
        return dayNumber && dayNumber[1] === searchTerm;
      })
    : waterCodes;

  const displayedWaterCodes = showAll ? filteredWaterCodes : filteredWaterCodes.slice(0);

  return (
    <div>
      <nav className="bg-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Link href="https://twitter.com/wateriscoding" className="text-black text-2xl font-bold"
          target='_blank'
          >
            WaterCodes
          </Link>
          <div className="flex items-center">
            <input
              type="text"
              placeholder="Search day..."
              className="px-3 py-1 rounded-md border-1 border-gray-200 bg-white text-orange-500 placeholder-orange-300 focus:border-orange-500 focus:ring-orange-500 transition duration-300 ease-in-out"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button
              className="ml-2 bg-orange-500 text-white px-4 py-1 rounded-md hover:bg-orange-600 transition duration-300 ease-in-out"
              onClick={() => {
                setSearchTerm('');
                setShowAll(false);
              }}
            >
              Clear
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {displayedWaterCodes.length > 0 ? (
          displayedWaterCodes.map((item: { Tweet: string, Link: string }, index: number) => {
            const dayNumber = item.Tweet.match(/Day (\d+) of ML:/)?.[1];
            const points = item.Tweet.split('\n').slice(1).map((point: string) => point.trim().replace(/^> /, ''));

            return (
              <div 
                key={index} 
                className="mb-8 rounded-lg shadow-md p-6 cursor-pointer hover:bg-gray-50 transition duration-300"
                onClick={() => window.open(item.Link, '_blank')}
              >
                <h2 className="text-2xl font-bold mb-4">
                  <span className="text-orange-500 hover:text-orange-600 transition duration-300">
                    Day {dayNumber} of ML
                  </span>
                </h2>
                <ul className="list-disc list-inside space-y-2">
                  {points.map((point, pointIndex) => (
                    <li key={pointIndex} className="text-gray-700">{point}</li>
                  ))}
                </ul>
              </div>
            );
          })
        ) : (
          <div className="text-center py-8">
            <p className="text-xl text-gray-600">No results found for Day {searchTerm} of ML.</p>
            <p className="mt-2 text-gray-500">Try searching for a different day or clear the search.</p>
          </div>
        )}
      </div>
    </div>
  );
}
