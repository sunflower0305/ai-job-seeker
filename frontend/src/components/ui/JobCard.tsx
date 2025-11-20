interface JobCardProps {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  experience: string;
  education: string;
  description?: string;
  onCollect?: () => void;
  onApply?: () => void;
}

export default function JobCard({
  id,
  title,
  company,
  location,
  salary,
  experience,
  education,
  description,
  onCollect,
  onApply,
}: JobCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all p-6 border-l-4 border-blue-600">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <a href={`/jobs/${id}`}>
            <h3 className="text-xl font-bold text-gray-900 hover:text-blue-600 cursor-pointer transition-colors">
              {title}
            </h3>
          </a>
          <p className="text-gray-600 mt-1">{company}</p>

          <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {location}
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              {experience}
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              {education}
            </span>
          </div>

          {description && (
            <p className="mt-3 text-gray-600 line-clamp-2">{description}</p>
          )}
        </div>

        <div className="ml-6 text-right">
          <div className="text-2xl font-bold text-orange-600 mb-4">{salary}</div>
          {(onCollect || onApply) && (
            <div className="flex flex-col gap-2">
              {onCollect && (
                <button
                  onClick={onCollect}
                  className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                >
                  收藏
                </button>
              )}
              {onApply && (
                <button
                  onClick={onApply}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  投递
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
