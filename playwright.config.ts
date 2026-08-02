import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  // No browser needed for pure logic tests
  projects: [
    {
      name: 'unit',
      use: {},
    },
  ],
  reporter: 'line',
})
