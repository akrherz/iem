module.exports = [
    {
        files: ["**/*.js"],
        languageOptions: {
            globals: {
                "$": false,
                "jQuery": false,
                "ol": false,
                "iemdata": false,
                "moment": false,
                "google": false
            }
        }
    }
];
