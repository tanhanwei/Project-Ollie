module.exports = {
	content: ['./src/routes/**/*.{svelte,js,ts}', './src/lib/components/*.{svelte,js,ts}'],
	plugins: [require('daisyui')],
	daisyui: {
		themes: [
			{
				'my-gemini-light': {
					primary: '#005AC1',
					'primary-content': '#FFFFFF',
					secondary: '#D8E2FF',
					'secondary-content': '#001A41',
					accent: '#5F52A7',
					'accent-content': '#E5DEFF',
					neutral: '#FFFFFF',
					'neutral-content': '#1B1B1F',
					'base-100': '#FFFFFF',
					'base-200': '#F9FAFB',
					'base-300': '#F4F5F7',
					'base-content': '#1B1B1F',
					info: '#1A73E8',
					success: '#34A853',
					warning: '#F9AB00',
					error: '#EA4335'
				}
			}
		]
	}
};
