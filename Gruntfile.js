module.exports = function (grunt) {
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        concat: {
            options: {
                separator: ';'
            },
            dist: {
                src: [
                    'tranny/static/vendor/modernizr/modernizr.js',
                    'tranny/static/vendor/moment/moment.js',
                    'tranny/static/vendor/lodash/dist/lodash.js',
                    'tranny/static/vendor/jquery/dist/jquery.js',
                    'tranny/static/vendor/socket.io-client/dist/socket.io.js',
                    'tranny/static/vendor/perfect-scrollbar/src/perfect-scrollbar.js',
                    'tranny/static/vendor/fastclick/lib/fastclick.js',
                    'tranny/static/vendor/foundation/js/foundation.js',
                    'tranny/static/vendor/highcharts/highcharts.js',
                    'tranny/static/js/highcharts-theme.js',
                    'tranny/static/js/context.js'
                ],
                dest: 'tranny/static/js/vendor/vendor.js'
            }
        },

        sass: {
            options: {
                includePaths: ['tranny/static/vendor/foundation/scss']
            },
            dist: {
                options: {
                    outputStyle: 'compressed'
                },
                files: {
                    'tranny/static/css/app.css': 'scss/app.scss'
                }
            }
        },

        coffee: {
            compileWithMaps: {
                options: {
                    sourceMap: true,
                    expand: true,
                    bare: true
                },
                files: {
                    'tranny/static/js/app.js': ['tranny/static/js/tranny.coffee', 'tranny/static/js/tranny-torrents.coffee'] // concat then compile into single file
                }
            }
        },

        watch: {
            grunt: { files: ['Gruntfile.js'] },

            sass: {
                files: 'scss/**/*.scss',
                tasks: ['sass']
            },

            coffee: {
                files: ['tranny/static/js/tranny.coffee', 'tranny/static/js/tranny-torrents.coffee'],
                tasks: 'coffee'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-coffee');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('build', ['sass', 'coffee', 'concat']);
    grunt.registerTask('default', ['build', 'watch', 'concat']);
};
