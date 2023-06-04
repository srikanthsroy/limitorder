from vyper.interfaces import ERC20

# interface Mintable:
#     def mint(_to: address, _value: uint256): nonpayable


struct ExactInputParams:
    path: Bytes[66]
    recipient: address
    deadline: uint256
    amountIn: uint256
    amountOutMinimum: uint256

interface UniswapV3SwapRouter:
    def exactInput(_params: ExactInputParams) -> uint256: payable


implements: UniswapV3SwapRouter


swap_was_called: public(bool)
excess_amount_out: public(uint256)

@payable
@external
def exactInput(_params: ExactInputParams) -> uint256:
    self.swap_was_called = True

    path: Bytes[66] = _params.path
    tokenIn: address = convert(slice(path, 0, 20), address)
    tokenOut: address = convert(slice(path, 46, 20), address)
    if (tokenOut == empty(address)):
        tokenOut = convert(slice(path, 23, 20), address)

    ERC20(tokenIn).transferFrom(msg.sender, self, _params.amountIn)

    # mint token out to self first to have sufficient liquidity
    # Mintable(_params.tokenOut).mint(self, _params.amountOutMinimum)

    amountOut: uint256 = _params.amountOutMinimum + self.excess_amount_out

    ERC20(tokenOut).transfer(msg.sender, amountOut)

    return amountOut

@external
def excessAmountOut(_excess: uint256):
    self.excess_amount_out = _excess