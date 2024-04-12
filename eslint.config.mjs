import globals from "globals";
import pluginJs from "@eslint/js";


export default [
    { files: ["**/*.js"], languageOptions: { sourceType: "script" } },
    {
        languageOptions: {
            globals: {
                $: "readonly", iemdata: "readonly", ol: "readonly", moment: "readonly",
                document: "readonly", window: "readonly", console: "readonly",
                google: "readonly", ...globals.browser
            }
        }
    },
    pluginJs.configs.recommended,
];