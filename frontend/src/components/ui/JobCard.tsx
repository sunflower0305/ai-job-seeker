interface JobCardProps {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  experience: string;
  education: string;
  description?: string;
  tags?: string[];
  isCollected?: boolean;
  onCollect?: () => void;
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
  tags,
  isCollected = false,
  onCollect,
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

          {tags && tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {tags.slice(0, 5).map((tag, index) => (
                <span key={index} className="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}

          {description && (
            <p className="mt-3 text-gray-600 line-clamp-2">{description}</p>
          )}
        </div>

        <div className="ml-6 text-right">
          <div className="text-2xl font-bold text-orange-600 mb-4">{salary}</div>
          {onCollect && (
            <button
              onClick={(e) => {
                e.preventDefault();
                onCollect();
              }}
              className={`flex items-center gap-2 px-4 py-2 text-sm border rounded-lg transition-all ${
                isCollected
                  ? 'border-yellow-500 bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                  : 'border-gray-300 text-gray-700 hover:border-yellow-500 hover:bg-yellow-50'
              }`}
            >
              <svg className="w-4 h-4" fill={isCollected ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              {isCollected ? '已收藏' : '收藏'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
