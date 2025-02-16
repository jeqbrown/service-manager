'use strict';
{
    function setTheme(mode) {
        document.documentElement.setAttribute('data-theme', mode);
        localStorage.setItem('theme', mode);
    }

    function cycleTheme() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (currentTheme === 'light') {
            setTheme('dark');
        } else if (currentTheme === 'dark') {
            setTheme('light');
        } else {
            setTheme(prefersDark ? 'light' : 'dark');
        }
    }

    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            setTheme(savedTheme);
        } else {
            setTheme('light');
        }
    }

    // Add event listener to theme toggle button
    document.addEventListener('DOMContentLoaded', function() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', cycleTheme);
        }
        initTheme();
    });
}