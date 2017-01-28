var autoprefixer = require('gulp-autoprefixer')
var plumber = require('gulp-plumber')
var gulp = require('gulp')
var gutil = require('gulp-util')
var sass = require('gulp-sass')

var onError = function (err) {
  gutil.beep()
  console.log(err.toString())
  this.emit('end')
}

/**
 * Styles
 */

var styles = {
  src: 'styles/**/*.scss',
  dest: '../catalog/static'
}

gulp.task('styles', function () {
  return gulp
    .src(styles.src)
    .pipe(plumber({errorHandler: onError}))
    .pipe(sass())
    .pipe(autoprefixer())
    .pipe(gulp.dest(styles.dest))
})

/**
 * Default
 */

gulp.task('default', [
  'styles',
], function () {
  gulp.watch(styles.src, ['styles'])
})
