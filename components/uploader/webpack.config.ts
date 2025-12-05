import path from 'path';
import {Configuration} from 'webpack';

const config = (_env: any, argv: any): Configuration => {
  const mode = argv.mode || 'development';
  const isProduction = mode === 'production';
  return {
    mode: mode,
    entry: './src/index.ts',

    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'uploader.js',
      library: {
        name: 'uploader',
        type: 'window',
      },
      clean: true,
    },

    resolve: {
      extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },

    module: {
      rules: [{
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      }, {
        test: /\.css?/i,
        use: ['style-loader', 'css-loader'],
      }],
    },

    externals: {
      react: 'React',
      'react-dom': 'ReactDOM',
      'prop-types': 'PropTypes',
    },

    devtool: isProduction ? 'source-map' : 'eval-source-map',
    optimization: {
      minimize: isProduction,
    },
  };
};

export default config;
