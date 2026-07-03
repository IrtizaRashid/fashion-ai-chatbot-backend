export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          <div>
            <h3 className="text-sm font-semibold text-black">About</h3>
            <p className="mt-4 text-sm text-gray-600">
              AI Fashion Stylist helps you find clothing that matches your body
              type and preferences.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-black">Links</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li>
                <a href="#" className="text-gray-600 hover:text-black">
                  Privacy
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-black">
                  Terms
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-black">Legal</h3>
            <p className="mt-4 text-sm text-gray-600">
              © 2024 AI Fashion Stylist. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
