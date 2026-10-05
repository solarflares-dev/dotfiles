return {
  {
    "kdheepak/monochrome.nvim",
    lazy = false,    -- Forces loading immediately on boot
    priority = 1000, -- Forces it to compile before any other UI modules
    config = function()
      -- Force standard background variables flat black
      vim.o.background = "dark"
      
      -- Load the colorscheme directly into the active engine buffer
      vim.cmd([[colorscheme monochrome]])
    end,
  },
}
