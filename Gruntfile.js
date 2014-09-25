module.exports = function (grunt) {
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        cssmin: {
            combine: {
                files: {
                    'tranny/static/css/app.min.css': [
                        'tranny/static/css/normalize.css',
                        'tranny/static/css/tranny.css',
                        'tranny/static/vendor/perfect-scrollbar/src/perfect-scrollbar.css',
                        'tranny/static/css/app.css'
                    ]
                }
            }
        },

        uglify: {
            release: {
                files: {
                    'tranny/static/js/vendor/vendor.min.js': ['tranny/static/js/vendor/vendor.js'],
                    'tranny/static/js/app.min.js': ['tranny/static/js/app.js']
                }
            }
        },

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
                    'tranny/static/js/vendor/context.js'
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
                    'tranny/static/js/app.js': [
                        'tranny/static/js/tranny.coffee',
                        'tranny/static/js/tranny-torrents.coffee',
                        'tranny/static/js/highcharts-theme.coffee'
                    ] // concat then compile into single file
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
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.registerTask('release', ['sass', 'coffee', 'concat', 'uglify:release', 'cssmin']);
    grunt.registerTask('build', ['sass', 'coffee', 'concat']);
    grunt.registerTask('default', ['build', 'watch', 'concat']);
};
