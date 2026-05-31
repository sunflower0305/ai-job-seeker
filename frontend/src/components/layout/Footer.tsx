export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* 关于我们 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">关于我们</h3>
            <p className="text-gray-400 text-sm">
              职位推荐平台致力于为求职者提供智能化、个性化的职位推荐服务，帮助您找到理想工作。
            </p>
          </div>

          {/* 快速链接 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">快速链接</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="/jobs"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  职位列表
                </a>
              </li>
              <li>
                <a
                  href="/recommendations"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  薪资预测
                </a>
              </li>
              <li>
                <a
                  href="/companies"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  企业列表
                </a>
              </li>
            </ul>
          </div>

          {/* 帮助支持 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">帮助支持</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="/help"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  使用帮助
                </a>
              </li>
              <li>
                <a
                  href="/privacy"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  隐私政策
                </a>
              </li>
              <li>
                <a
                  href="/terms"
                  className="text-gray-400 hover:text-white text-sm transition-colors"
                >
                  服务条款
                </a>
              </li>
            </ul>
          </div>

          {/* 联系我们 */}
          <div>
            <h3 className="text-lg font-semibold mb-4">联系我们</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>邮箱: contact@zhangleyang.com</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800">
          <p className="text-center text-gray-400 text-sm">
            © 2026 职位推荐平台. All rights reserved. | Next.js + TypeScript +
            Tailwind CSS
          </p>
        </div>
      </div>
    </footer>
  );
}
